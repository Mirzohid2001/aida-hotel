from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from hotel.utils import OptimizeImagesMixin


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Updated at"), auto_now=True)

    class Meta:
        abstract = True


class SiteSettings(OptimizeImagesMixin, models.Model):
    class Currency(models.TextChoices):
        UZS = "UZS", _("UZS (so'm)")
        USD = "USD", _("USD ($)")

    image_optimize_fields = ("logo", "og_image")
    image_max_side = 1200
    image_quality = 85

    site_name = models.CharField(_("Site name"), max_length=120, default="Aida Hotel")
    tagline = models.CharField(_("Tagline"), max_length=255, blank=True)
    logo = models.ImageField(_("Logo"), upload_to="site/", blank=True, null=True)
    phone = models.CharField(_("Phone"), max_length=32, blank=True)
    email = models.EmailField(_("Email"), blank=True)
    address = models.TextField(_("Address"), blank=True)
    currency = models.CharField(
        _("Currency"),
        max_length=3,
        choices=Currency.choices,
        default=Currency.UZS,
        help_text=_("Shown next to all room prices on the website and in admin."),
    )
    check_in_time = models.CharField(_("Check-in time"), max_length=16, default="14:00")
    check_out_time = models.CharField(_("Check-out time"), max_length=16, default="12:00")
    map_latitude = models.DecimalField(
        _("Map latitude"), max_digits=9, decimal_places=6, null=True, blank=True
    )
    map_longitude = models.DecimalField(
        _("Map longitude"), max_digits=9, decimal_places=6, null=True, blank=True
    )
    facebook_url = models.URLField(_("Facebook URL"), blank=True)
    instagram_url = models.URLField(_("Instagram URL"), blank=True)
    telegram_url = models.URLField(_("Telegram URL"), blank=True)
    google_analytics_id = models.CharField(_("Google Analytics ID"), max_length=64, blank=True)
    yandex_metrika_id = models.CharField(_("Yandex Metrika ID"), max_length=64, blank=True)
    telegram_bot_token = models.CharField(
        _("Telegram bot token"),
        max_length=128,
        blank=True,
        help_text=_("From @BotFather, e.g. 123456789:ABCdef..."),
    )
    telegram_chat_id = models.CharField(
        _("Telegram chat ID"),
        max_length=64,
        blank=True,
        help_text=_("Group or channel chat ID, e.g. -1001234567890"),
    )
    telegram_notifications_enabled = models.BooleanField(
        _("Telegram notifications"),
        default=False,
        help_text=_("Send a Telegram message when a new booking is submitted."),
    )
    meta_title = models.CharField(_("Meta title"), max_length=255, blank=True)
    meta_description = models.TextField(_("Meta description"), blank=True)
    og_image = models.ImageField(_("OG image"), upload_to="site/", blank=True, null=True)

    class Meta:
        verbose_name = _("Site settings")
        verbose_name_plural = _("Site settings")

    def __str__(self):
        return self.site_name

    @property
    def currency_label(self):
        if self.currency == self.Currency.USD:
            return "$"
        return "UZS"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class HeroSlide(OptimizeImagesMixin, models.Model):
    image_optimize_fields = ("image",)

    title = models.CharField(_("Title"), max_length=200)
    subtitle = models.CharField(_("Subtitle"), max_length=255, blank=True)
    image = models.ImageField(
        _("Image"),
        upload_to="hero/",
        help_text=_("Large photos are auto-resized (max ~1920px) to speed up upload."),
    )
    cta_text = models.CharField(_("CTA text"), max_length=64, blank=True)
    cta_url = models.CharField(_("CTA URL"), max_length=255, blank=True, default="/book/")
    ordering = models.PositiveIntegerField(_("Ordering"), default=0)
    is_active = models.BooleanField(_("Active"), default=True)

    class Meta:
        ordering = ["ordering", "id"]
        verbose_name = _("Hero slide")
        verbose_name_plural = _("Hero slides")

    def __str__(self):
        return self.title


class AboutSection(OptimizeImagesMixin, models.Model):
    image_optimize_fields = ("image",)

    title = models.CharField(_("Title"), max_length=200)
    content = models.TextField(_("Content"))
    image = models.ImageField(_("Image"), upload_to="about/", blank=True, null=True)

    class Meta:
        verbose_name = _("About section")
        verbose_name_plural = _("About section")

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1, defaults={"title": "Aida Hotel", "content": ""})
        return obj


class Amenity(models.Model):
    name = models.CharField(_("Name"), max_length=120)
    description = models.TextField(_("Description"), blank=True)
    icon = models.CharField(_("Icon"), max_length=64, blank=True)
    ordering = models.PositiveIntegerField(_("Ordering"), default=0)
    is_active = models.BooleanField(_("Active"), default=True)

    class Meta:
        ordering = ["ordering", "id"]
        verbose_name = _("Amenity")
        verbose_name_plural = _("Amenities")

    def __str__(self):
        return self.name


class GalleryImage(OptimizeImagesMixin, models.Model):
    image_optimize_fields = ("image",)

    title = models.CharField(_("Title"), max_length=200, blank=True)
    image = models.ImageField(
        _("Image"),
        upload_to="gallery/",
        help_text=_("Large photos are auto-resized (max ~1920px) to speed up upload."),
    )
    caption = models.CharField(_("Caption"), max_length=255, blank=True)
    ordering = models.PositiveIntegerField(_("Ordering"), default=0)
    is_active = models.BooleanField(_("Active"), default=True)

    class Meta:
        ordering = ["ordering", "id"]
        verbose_name = _("Gallery image")
        verbose_name_plural = _("Gallery images")

    def __str__(self):
        return self.title or f"Gallery #{self.pk}"


class Testimonial(models.Model):
    guest_name = models.CharField(_("Guest name"), max_length=120)
    content = models.TextField(_("Content"))
    rating = models.PositiveSmallIntegerField(_("Rating"), default=5)
    ordering = models.PositiveIntegerField(_("Ordering"), default=0)
    is_active = models.BooleanField(_("Active"), default=True)

    class Meta:
        ordering = ["ordering", "id"]
        verbose_name = _("Testimonial")
        verbose_name_plural = _("Testimonials")

    def __str__(self):
        return self.guest_name


class FAQ(models.Model):
    question = models.CharField(_("Question"), max_length=255)
    answer = models.TextField(_("Answer"))
    ordering = models.PositiveIntegerField(_("Ordering"), default=0)
    is_active = models.BooleanField(_("Active"), default=True)

    class Meta:
        ordering = ["ordering", "id"]
        verbose_name = _("FAQ")
        verbose_name_plural = _("FAQs")

    def __str__(self):
        return self.question


class Promotion(models.Model):
    title = models.CharField(_("Title"), max_length=200)
    description = models.TextField(_("Description"), blank=True)
    discount_label = models.CharField(_("Discount label"), max_length=64, blank=True)
    is_active = models.BooleanField(_("Active"), default=True)
    starts_at = models.DateField(_("Starts at"), null=True, blank=True)
    ends_at = models.DateField(_("Ends at"), null=True, blank=True)

    class Meta:
        ordering = ["-starts_at", "id"]
        verbose_name = _("Promotion")
        verbose_name_plural = _("Promotions")

    def __str__(self):
        return self.title


class StatHighlight(models.Model):
    value = models.CharField(_("Value"), max_length=64)
    label = models.CharField(_("Label"), max_length=120)
    ordering = models.PositiveIntegerField(_("Ordering"), default=0)
    is_active = models.BooleanField(_("Active"), default=True)

    class Meta:
        ordering = ["ordering", "id"]
        verbose_name = _("Stat highlight")
        verbose_name_plural = _("Stat highlights")

    def __str__(self):
        return f"{self.value} — {self.label}"


class NearbyPlace(models.Model):
    name = models.CharField(_("Name"), max_length=200)
    distance = models.CharField(_("Distance"), max_length=64, blank=True)
    icon = models.CharField(_("Icon"), max_length=64, blank=True)
    ordering = models.PositiveIntegerField(_("Ordering"), default=0)
    is_active = models.BooleanField(_("Active"), default=True)

    class Meta:
        ordering = ["ordering", "id"]
        verbose_name = _("Nearby place")
        verbose_name_plural = _("Nearby places")

    def __str__(self):
        return self.name


class PolicyPage(models.Model):
    title = models.CharField(_("Title"), max_length=200)
    slug = models.SlugField(_("Slug"), unique=True)
    content = models.TextField(_("Content"))
    is_active = models.BooleanField(_("Active"), default=True)

    class Meta:
        ordering = ["title"]
        verbose_name = _("Policy page")
        verbose_name_plural = _("Policy pages")

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class ContactMessage(TimeStampedModel):
    name = models.CharField(_("Name"), max_length=120)
    email = models.EmailField(_("Email"))
    phone = models.CharField(_("Phone"), max_length=32, blank=True)
    message = models.TextField(_("Message"))
    is_read = models.BooleanField(_("Read"), default=False)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("Contact message")
        verbose_name_plural = _("Contact messages")

    def __str__(self):
        return f"{self.name} — {self.email}"


class RoomType(models.Model):
    name = models.CharField(_("Name"), max_length=120)
    slug = models.SlugField(_("Slug"), unique=True)
    description = models.TextField(_("Description"), blank=True)
    base_price = models.DecimalField(
        _("Base price"),
        max_digits=10,
        decimal_places=2,
        help_text=_("Per night. Currency is set in Site settings (UZS or USD)."),
    )
    capacity = models.PositiveSmallIntegerField(_("Capacity"), default=2)
    size_sqm = models.PositiveSmallIntegerField(_("Size (m²)"), null=True, blank=True)
    is_active = models.BooleanField(_("Active"), default=True)
    ordering = models.PositiveIntegerField(_("Ordering"), default=0)

    class Meta:
        ordering = ["ordering", "base_price"]
        verbose_name = _("Room type")
        verbose_name_plural = _("Room types")

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Room(models.Model):
    room_type = models.ForeignKey(
        RoomType,
        on_delete=models.CASCADE,
        related_name="rooms",
        verbose_name=_("Room type"),
    )
    number = models.CharField(_("Number"), max_length=16)
    floor = models.PositiveSmallIntegerField(_("Floor"), default=1)
    is_active = models.BooleanField(_("Active"), default=True)

    class Meta:
        ordering = ["floor", "number"]
        unique_together = [("room_type", "number")]
        verbose_name = _("Room")
        verbose_name_plural = _("Rooms")

    def __str__(self):
        return f"{self.number} ({self.room_type.name})"


class RoomImage(OptimizeImagesMixin, models.Model):
    image_optimize_fields = ("image",)

    room_type = models.ForeignKey(
        RoomType,
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name=_("Room type"),
    )
    image = models.ImageField(
        _("Image"),
        upload_to="rooms/",
        help_text=_("Large photos are auto-resized (max ~1920px) to speed up upload."),
    )
    caption = models.CharField(_("Caption"), max_length=255, blank=True)
    ordering = models.PositiveIntegerField(_("Ordering"), default=0)
    is_primary = models.BooleanField(_("Primary"), default=False)

    class Meta:
        ordering = ["ordering", "id"]
        verbose_name = _("Room image")
        verbose_name_plural = _("Room images")

    def __str__(self):
        return self.caption or f"{self.room_type.name} image"


class SeasonalPrice(models.Model):
    room_type = models.ForeignKey(
        RoomType,
        on_delete=models.CASCADE,
        related_name="seasonal_prices",
        verbose_name=_("Room type"),
    )
    start_date = models.DateField(_("Start date"))
    end_date = models.DateField(_("End date"))
    price = models.DecimalField(
        _("Price"),
        max_digits=10,
        decimal_places=2,
        help_text=_("Per night. Uses the currency from Site settings."),
    )

    class Meta:
        ordering = ["start_date"]
        verbose_name = _("Seasonal price")
        verbose_name_plural = _("Seasonal prices")

    def __str__(self):
        return f"{self.room_type.name}: {self.start_date} — {self.end_date}"

    def clean(self):
        if self.end_date <= self.start_date:
            raise ValidationError(_("End date must be after start date."))


class BlockedDate(models.Model):
    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        related_name="blocked_dates",
        verbose_name=_("Room"),
    )
    start_date = models.DateField(_("Start date"))
    end_date = models.DateField(_("End date"))
    reason = models.CharField(_("Reason"), max_length=255, blank=True)

    class Meta:
        ordering = ["start_date"]
        verbose_name = _("Blocked date")
        verbose_name_plural = _("Blocked dates")

    def __str__(self):
        return f"{self.room.number}: {self.start_date} — {self.end_date}"

    def clean(self):
        if self.end_date <= self.start_date:
            raise ValidationError(_("End date must be after start date."))


class Booking(TimeStampedModel):
    class Status(models.TextChoices):
        PENDING = "pending", _("Pending")
        CONFIRMED = "confirmed", _("Confirmed")
        CANCELLED = "cancelled", _("Cancelled")
        COMPLETED = "completed", _("Completed")

    reference_code = models.CharField(
        _("Reference code"), max_length=32, unique=True, editable=False
    )
    guest_name = models.CharField(_("Guest name"), max_length=120)
    email = models.EmailField(_("Email"))
    phone = models.CharField(_("Phone"), max_length=32)
    guests_count = models.PositiveSmallIntegerField(_("Guests"), default=1)
    check_in = models.DateField(_("Check-in"))
    check_out = models.DateField(_("Check-out"))
    special_requests = models.TextField(_("Special requests"), blank=True)
    estimated_total = models.DecimalField(
        _("Estimated total"), max_digits=12, decimal_places=2, default=Decimal("0.00")
    )
    status = models.CharField(
        _("Status"), max_length=16, choices=Status.choices, default=Status.PENDING
    )
    notes = models.TextField(_("Internal notes"), blank=True)
    rooms = models.ManyToManyField(
        Room, through="BookingRoom", related_name="bookings", verbose_name=_("Rooms")
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("Booking")
        verbose_name_plural = _("Bookings")

    def __str__(self):
        return self.reference_code

    def clean(self):
        if self.check_out <= self.check_in:
            raise ValidationError(_("Check-out must be after check-in."))


class BookingRoom(models.Model):
    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        related_name="booking_rooms",
        verbose_name=_("Booking"),
    )
    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        related_name="booking_rooms",
        verbose_name=_("Room"),
    )
    nightly_rate = models.DecimalField(_("Nightly rate"), max_digits=10, decimal_places=2)

    class Meta:
        unique_together = [("booking", "room")]
        verbose_name = _("Booking room")
        verbose_name_plural = _("Booking rooms")

    def __str__(self):
        return f"{self.booking.reference_code} — {self.room.number}"
