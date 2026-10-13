import re
import time
from datetime import date

from django import forms
from django.core.cache import cache
from django.utils.translation import gettext_lazy as _

from hotel.models import ContactMessage, RoomType, Testimonial
from hotel.services.availability import get_available_rooms
from hotel.services.booking import validate_booking_dates

_URL_RE = re.compile(r"https?://|www\.", re.I)


class HoneypotMixin:
    """Adds spam honeypot cleaning. Subclasses must declare `website` as a form field."""

    def clean_website(self):
        if self.cleaned_data.get("website"):
            raise forms.ValidationError(_("Invalid submission."))
        return ""


class BookingForm(HoneypotMixin, forms.Form):
    website = forms.CharField(
        required=False,
        widget=forms.HiddenInput(attrs={"tabindex": "-1", "autocomplete": "off"}),
    )
    room_type = forms.ModelChoiceField(
        queryset=RoomType.objects.filter(is_active=True),
        label=_("Room type"),
        widget=forms.Select(attrs={"class": "form-control", "data-capacity-source": "1"}),
    )
    check_in = forms.DateField(
        label=_("Check-in"),
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control", "min": date.today().isoformat()}),
    )
    check_out = forms.DateField(
        label=_("Check-out"),
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control", "min": date.today().isoformat()}),
    )
    guest_name = forms.CharField(max_length=120, label=_("Full name"), widget=forms.TextInput(attrs={"class": "form-control", "autocomplete": "name"}))
    email = forms.EmailField(label=_("Email"), widget=forms.EmailInput(attrs={"class": "form-control", "autocomplete": "email"}))
    phone = forms.CharField(max_length=32, label=_("Phone"), widget=forms.TextInput(attrs={"class": "form-control", "autocomplete": "tel"}))
    guests_count = forms.IntegerField(min_value=1, max_value=10, initial=1, label=_("Guests"), widget=forms.NumberInput(attrs={"class": "form-control", "min": "1", "max": "10"}))
    special_requests = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 3, "class": "form-control", "placeholder": ""}),
        label=_("Special requests"),
    )
    room_ids = forms.CharField(required=False, widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        today = date.today().isoformat()
        self.fields["check_in"].widget.attrs["min"] = today
        self.fields["check_out"].widget.attrs["min"] = today
        room_type_field = self.fields["room_type"]
        room_type_field.queryset = RoomType.objects.filter(is_active=True)
        # Encode capacity on each option via label data handled in template JS

    def clean(self):
        cleaned = super().clean()
        check_in = cleaned.get("check_in")
        check_out = cleaned.get("check_out")
        room_type = cleaned.get("room_type")

        if check_in and check_out:
            try:
                validate_booking_dates(check_in, check_out)
            except Exception as exc:
                raise forms.ValidationError(str(exc))

            if check_in < date.today():
                raise forms.ValidationError(_("Check-in date cannot be in the past."))

        if room_type and check_in and check_out:
            raw_ids = cleaned.get("room_ids", "")
            ids = [int(x) for x in raw_ids.split(",") if x.strip().isdigit()]
            if not ids:
                raise forms.ValidationError(_("Please select at least one available room."))
            available = {r.pk for r in get_available_rooms(room_type, check_in, check_out)}
            if not set(ids).issubset(available):
                raise forms.ValidationError(_("Selected rooms are not available for these dates."))
            cleaned["selected_room_ids"] = ids

        return cleaned

    def get_selected_room_ids(self):
        return self.cleaned_data.get("selected_room_ids", [])


class ContactForm(HoneypotMixin, forms.ModelForm):
    website = forms.CharField(
        required=False,
        widget=forms.HiddenInput(attrs={"tabindex": "-1", "autocomplete": "off"}),
    )

    class Meta:
        model = ContactMessage
        fields = ["name", "email", "phone", "message"]
        labels = {
            "name": _("Name"),
            "email": _("Email"),
            "phone": _("Phone"),
            "message": _("Message"),
        }
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "autocomplete": "name"}),
            "email": forms.EmailInput(attrs={"class": "form-control", "autocomplete": "email"}),
            "phone": forms.TextInput(attrs={"class": "form-control", "autocomplete": "tel"}),
            "message": forms.Textarea(attrs={"rows": 5, "class": "form-control"}),
        }

    def save(self, commit=True):
        return super().save(commit=commit)


class ReviewForm(HoneypotMixin, forms.ModelForm):
    """Public guest review — published only after admin approval."""

    website = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "tabindex": "-1",
                "autocomplete": "off",
                "class": "form-honeypot",
                "aria-hidden": "true",
            }
        ),
    )
    form_ts = forms.CharField(required=False, widget=forms.HiddenInput)

    class Meta:
        model = Testimonial
        fields = ["guest_name", "email", "rating", "content"]
        labels = {
            "guest_name": _("Your name"),
            "email": _("Email"),
            "rating": _("Rating"),
            "content": _("Your review"),
        }
        widgets = {
            "guest_name": forms.TextInput(
                attrs={"class": "form-control", "autocomplete": "name", "maxlength": "80"}
            ),
            "email": forms.EmailInput(
                attrs={"class": "form-control", "autocomplete": "email"}
            ),
            "rating": forms.Select(
                choices=[(i, "★" * i) for i in range(5, 0, -1)],
                attrs={"class": "form-control"},
            ),
            "content": forms.Textarea(
                attrs={
                    "rows": 4,
                    "class": "form-control",
                    "maxlength": "800",
                    "placeholder": _("Share your experience at Aida Hotel…"),
                }
            ),
        }

    def __init__(self, *args, client_ip: str | None = None, **kwargs):
        self.client_ip = client_ip or "unknown"
        super().__init__(*args, **kwargs)
        self.fields["email"].required = True
        self.fields["rating"].initial = 5
        if not self.is_bound:
            self.fields["form_ts"].initial = str(int(time.time()))

    def clean_guest_name(self):
        name = (self.cleaned_data.get("guest_name") or "").strip()
        if len(name) < 2:
            raise forms.ValidationError(_("Please enter your name."))
        if _URL_RE.search(name):
            raise forms.ValidationError(_("Invalid submission."))
        return name[:80]

    def clean_content(self):
        content = (self.cleaned_data.get("content") or "").strip()
        if len(content) < 15:
            raise forms.ValidationError(_("Please write a slightly longer review."))
        if len(content) > 800:
            raise forms.ValidationError(_("Review is too long."))
        if len(_URL_RE.findall(content)) > 0:
            raise forms.ValidationError(_("Links are not allowed in reviews."))
        return content

    def clean_rating(self):
        rating = self.cleaned_data.get("rating") or 5
        try:
            rating = int(rating)
        except (TypeError, ValueError):
            rating = 5
        if rating < 1 or rating > 5:
            raise forms.ValidationError(_("Choose a rating from 1 to 5."))
        return rating

    def clean(self):
        cleaned = super().clean()
        raw_ts = (cleaned.get("form_ts") or "").strip()
        try:
            started = int(raw_ts)
        except (TypeError, ValueError):
            raise forms.ValidationError(_("Invalid submission."))
        elapsed = time.time() - started
        if elapsed < 3:
            raise forms.ValidationError(_("Please take a moment before submitting."))
        if elapsed > 60 * 60 * 6:
            raise forms.ValidationError(_("Form expired. Please reload the page."))

        cache_key = f"review_rate:{self.client_ip}"
        if (cache.get(cache_key) or 0) >= 3:
            raise forms.ValidationError(
                _("Too many reviews from this device today. Please try again tomorrow.")
            )
        return cleaned

    def save(self, commit=True):
        review = super().save(commit=False)
        review.source = Testimonial.Source.GUEST
        review.is_active = False
        review.ordering = 0
        if commit:
            review.save()
            cache_key = f"review_rate:{self.client_ip}"
            count = cache.get(cache_key) or 0
            cache.set(cache_key, count + 1, timeout=60 * 60 * 24)
        return review
