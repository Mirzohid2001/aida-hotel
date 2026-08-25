from datetime import date

from django import forms
from django.utils.translation import gettext_lazy as _

from hotel.models import ContactMessage, RoomType
from hotel.services.availability import get_available_rooms
from hotel.services.booking import validate_booking_dates


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
