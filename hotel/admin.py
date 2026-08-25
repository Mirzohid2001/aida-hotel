from django.contrib import admin, messages
from django.db.models import Count, Q
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from hotel.models import (
    AboutSection,
    Amenity,
    BlockedDate,
    Booking,
    BookingRoom,
    ContactMessage,
    FAQ,
    GalleryImage,
    HeroSlide,
    NearbyPlace,
    PolicyPage,
    Promotion,
    Room,
    RoomImage,
    RoomType,
    SeasonalPrice,
    SiteSettings,
    StatHighlight,
    Testimonial,
)


# ── helpers ──────────────────────────────────────────────────────────────────


def _thumb(image_field, size=48):
    if not image_field:
        return format_html('<span class="aida-muted">—</span>')
    return format_html(
        '<img src="{}" class="aida-thumb" width="{}" height="{}" alt="" />',
        image_field.url,
        size,
        size,
    )


def _bool_badge(value, yes=_("Active"), no=_("Off")):
    if value:
        return format_html('<span class="aida-badge aida-badge--ok">{}</span>', yes)
    return format_html('<span class="aida-badge aida-badge--off">{}</span>', no)


def _status_badge(status):
    css = {
        Booking.Status.PENDING: "aida-badge--warn",
        Booking.Status.CONFIRMED: "aida-badge--ok",
        Booking.Status.CANCELLED: "aida-badge--danger",
        Booking.Status.COMPLETED: "aida-badge--info",
    }.get(status, "aida-badge--off")
    label = dict(Booking.Status.choices).get(status, status)
    return format_html('<span class="aida-badge {}">{}</span>', css, label)


# ── base mixins ──────────────────────────────────────────────────────────────


class SingletonAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        if self.model.objects.exists():
            return False
        return super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        return False


class OrderedActiveAdmin(admin.ModelAdmin):
    list_editable = ("ordering", "is_active")
    list_filter = ("is_active",)
    ordering = ("ordering", "id")


# ── site content ─────────────────────────────────────────────────────────────


@admin.register(SiteSettings)
class SiteSettingsAdmin(SingletonAdmin):
    fieldsets = (
        (
            _("Brand"),
            {"fields": ("site_name", "tagline", "logo")},
        ),
        (
            _("Contact"),
            {"fields": ("phone", "email", "address")},
        ),
        (
            _("Pricing"),
            {
                "fields": ("currency",),
                "description": _(
                    "Choose UZS or USD ($). This label is shown on all room prices."
                ),
            },
        ),
        (
            _("Hours"),
            {"fields": ("check_in_time", "check_out_time")},
        ),
        (
            _("Map"),
            {"fields": ("map_latitude", "map_longitude")},
        ),
        (
            _("Social links"),
            {"fields": ("facebook_url", "instagram_url", "telegram_url")},
        ),
        (
            _("Telegram notifications"),
            {
                "fields": (
                    "telegram_notifications_enabled",
                    "telegram_bot_token",
                    "telegram_chat_id",
                ),
                "description": _(
                    "Create a bot with @BotFather, add it to your group, then paste the bot token "
                    "and group chat ID (usually starts with -100)."
                ),
            },
        ),
        (
            _("SEO & analytics"),
            {
                "fields": (
                    "meta_title",
                    "meta_description",
                    "og_image",
                    "google_analytics_id",
                    "yandex_metrika_id",
                ),
            },
        ),
    )


@admin.register(AboutSection)
class AboutSectionAdmin(SingletonAdmin):
    fieldsets = (
        (None, {"fields": ("title", "content", "image")}),
    )
    readonly_fields = ("image_preview",)

    @admin.display(description=_("Preview"))
    def image_preview(self, obj):
        return _thumb(obj.image, 160)

    def get_fieldsets(self, request, obj=None):
        if obj and obj.image:
            return ((None, {"fields": ("title", "content", "image", "image_preview")}),)
        return self.fieldsets


@admin.register(HeroSlide)
class HeroSlideAdmin(OrderedActiveAdmin):
    list_display = ("thumb", "title", "ordering", "is_active")
    search_fields = ("title", "subtitle")
    fieldsets = (
        (None, {"fields": ("title", "subtitle", "image")}),
        (_("Call to action"), {"fields": ("cta_text", "cta_url")}),
        (_("Display"), {"fields": ("ordering", "is_active")}),
    )

    @admin.display(description=_("Image"))
    def thumb(self, obj):
        return _thumb(obj.image)


@admin.register(Amenity)
class AmenityAdmin(OrderedActiveAdmin):
    list_display = ("name", "icon", "ordering", "is_active")
    search_fields = ("name", "description")
    fieldsets = (
        (None, {"fields": ("name", "description", "icon")}),
        (_("Display"), {"fields": ("ordering", "is_active")}),
    )


@admin.register(GalleryImage)
class GalleryImageAdmin(OrderedActiveAdmin):
    list_display = ("thumb", "title", "ordering", "is_active")
    search_fields = ("title", "caption")
    fieldsets = (
        (None, {"fields": ("title", "image", "caption")}),
        (_("Display"), {"fields": ("ordering", "is_active")}),
    )

    @admin.display(description=_("Image"))
    def thumb(self, obj):
        return _thumb(obj.image)


@admin.register(Testimonial)
class TestimonialAdmin(OrderedActiveAdmin):
    list_display = ("guest_name", "stars", "ordering", "is_active")
    search_fields = ("guest_name", "content")
    list_filter = ("is_active", "rating")
    fieldsets = (
        (None, {"fields": ("guest_name", "content", "rating")}),
        (_("Display"), {"fields": ("ordering", "is_active")}),
    )

    @admin.display(description=_("Rating"), ordering="rating")
    def stars(self, obj):
        filled = "★" * int(obj.rating or 0)
        empty = "☆" * max(0, 5 - int(obj.rating or 0))
        return format_html('<span class="aida-stars">{}{}</span>', filled, empty)


@admin.register(FAQ)
class FAQAdmin(OrderedActiveAdmin):
    list_display = ("question", "ordering", "is_active")
    search_fields = ("question", "answer")
    fieldsets = (
        (None, {"fields": ("question", "answer")}),
        (_("Display"), {"fields": ("ordering", "is_active")}),
    )


@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ("title", "discount_label", "starts_at", "ends_at", "is_active")
    list_filter = ("is_active",)
    list_editable = ("is_active",)
    search_fields = ("title", "description", "discount_label")
    date_hierarchy = "starts_at"
    fieldsets = (
        (None, {"fields": ("title", "description", "discount_label")}),
        (_("Schedule"), {"fields": ("starts_at", "ends_at", "is_active")}),
    )


@admin.register(StatHighlight)
class StatHighlightAdmin(OrderedActiveAdmin):
    list_display = ("value", "label", "ordering", "is_active")
    search_fields = ("value", "label")


@admin.register(NearbyPlace)
class NearbyPlaceAdmin(OrderedActiveAdmin):
    list_display = ("name", "distance", "icon", "ordering", "is_active")
    search_fields = ("name", "distance")


@admin.register(PolicyPage)
class PolicyPageAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "active_badge")
    list_filter = ("is_active",)
    search_fields = ("title", "slug", "content")
    prepopulated_fields = {"slug": ("title",)}
    fieldsets = (
        (None, {"fields": ("title", "slug", "content", "is_active")}),
    )

    @admin.display(description=_("Status"))
    def active_badge(self, obj):
        return _bool_badge(obj.is_active)


# ── inbox ────────────────────────────────────────────────────────────────────


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "phone", "read_badge", "created_at")
    list_filter = ("is_read", "created_at")
    search_fields = ("name", "email", "phone", "message")
    readonly_fields = ("name", "email", "phone", "message", "created_at", "updated_at")
    date_hierarchy = "created_at"
    actions = ["mark_as_read", "mark_as_unread"]
    fieldsets = (
        (_("Sender"), {"fields": ("name", "email", "phone")}),
        (_("Message"), {"fields": ("message", "is_read")}),
        (_("Meta"), {"fields": ("created_at", "updated_at")}),
    )

    @admin.display(description=_("Status"), ordering="is_read")
    def read_badge(self, obj):
        if obj.is_read:
            return format_html('<span class="aida-badge aida-badge--info">{}</span>', _("Read"))
        return format_html('<span class="aida-badge aida-badge--warn">{}</span>', _("New"))

    @admin.action(description=_("Mark selected as read"))
    def mark_as_read(self, request, queryset):
        updated = queryset.update(is_read=True)
        self.message_user(
            request,
            _("%(count)d message(s) marked as read.") % {"count": updated},
            messages.SUCCESS,
        )

    @admin.action(description=_("Mark selected as unread"))
    def mark_as_unread(self, request, queryset):
        updated = queryset.update(is_read=False)
        self.message_user(
            request,
            _("%(count)d message(s) marked as unread.") % {"count": updated},
            messages.SUCCESS,
        )

    def change_view(self, request, object_id, form_url="", extra_context=None):
        ContactMessage.objects.filter(pk=object_id, is_read=False).update(is_read=True)
        return super().change_view(request, object_id, form_url, extra_context)


# ── rooms ────────────────────────────────────────────────────────────────────


class RoomInline(admin.TabularInline):
    model = Room
    extra = 0
    fields = ("number", "floor", "is_active")
    show_change_link = True


class RoomImageInline(admin.TabularInline):
    model = RoomImage
    extra = 0
    fields = ("thumb", "image", "caption", "ordering", "is_primary")
    readonly_fields = ("thumb",)
    show_change_link = False

    @admin.display(description=_("Preview"))
    def thumb(self, obj):
        return _thumb(getattr(obj, "image", None), 40)


class SeasonalPriceInline(admin.TabularInline):
    model = SeasonalPrice
    extra = 0
    fields = ("start_date", "end_date", "price")


class BlockedDateInline(admin.TabularInline):
    model = BlockedDate
    extra = 0
    fields = ("start_date", "end_date", "reason")


@admin.register(RoomType)
class RoomTypeAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "base_price_display",
        "capacity",
        "room_count",
        "is_active",
        "ordering",
    )
    list_editable = ("is_active", "ordering")
    list_filter = ("is_active",)
    search_fields = ("name", "slug", "description")
    prepopulated_fields = {"slug": ("name",)}
    filter_horizontal = ()
    inlines = [RoomInline, RoomImageInline, SeasonalPriceInline]
    fieldsets = (
        (None, {"fields": ("name", "slug", "description")}),
        (
            _("Pricing & capacity"),
            {
                "fields": ("base_price", "capacity", "size_sqm"),
                "description": _(
                    "Enter the nightly price as a number. Set UZS or USD ($) under "
                    "Site settings → Pricing."
                ),
            },
        ),
        (_("Display"), {"fields": ("ordering", "is_active")}),
    )

    @admin.display(description=_("Base price"), ordering="base_price")
    def base_price_display(self, obj):
        label = SiteSettings.load().currency_label
        return f"{obj.base_price} {label}"

    @admin.display(description=_("Rooms"))
    def room_count(self, obj):
        return obj.rooms.count()

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(_rooms=Count("rooms"))


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ("number", "room_type", "floor", "active_badge")
    list_filter = ("room_type", "floor", "is_active")
    search_fields = ("number", "room_type__name")
    list_select_related = ("room_type",)
    inlines = [BlockedDateInline]
    fieldsets = (
        (None, {"fields": ("room_type", "number", "floor", "is_active")}),
    )

    @admin.display(description=_("Status"), ordering="is_active")
    def active_badge(self, obj):
        return _bool_badge(obj.is_active)


# ── bookings ─────────────────────────────────────────────────────────────────


class BookingRoomInline(admin.TabularInline):
    model = BookingRoom
    extra = 0
    readonly_fields = ("room", "nightly_rate")
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        "reference_code",
        "guest_name",
        "stay_dates",
        "guests_count",
        "status_badge",
        "estimated_total",
        "created_at",
    )
    list_filter = ("status", "check_in", "created_at")
    search_fields = ("reference_code", "guest_name", "email", "phone")
    readonly_fields = (
        "reference_code",
        "created_at",
        "updated_at",
        "estimated_total",
        "status_badge",
    )
    date_hierarchy = "check_in"
    inlines = [BookingRoomInline]
    actions = ["confirm_bookings", "cancel_bookings", "complete_bookings"]
    list_per_page = 25
    fieldsets = (
        (
            _("Guest"),
            {"fields": ("guest_name", "email", "phone", "guests_count")},
        ),
        (
            _("Stay"),
            {"fields": ("check_in", "check_out", "special_requests")},
        ),
        (
            _("Status & total"),
            {"fields": ("status", "estimated_total", "notes")},
        ),
        (
            _("System"),
            {"fields": ("reference_code", "created_at", "updated_at")},
        ),
    )

    @admin.display(description=_("Dates"), ordering="check_in")
    def stay_dates(self, obj):
        return format_html(
            '<span class="aida-dates">{} → {}</span>',
            obj.check_in.strftime("%d.%m.%Y"),
            obj.check_out.strftime("%d.%m.%Y"),
        )

    @admin.display(description=_("Status"), ordering="status")
    def status_badge(self, obj):
        return _status_badge(obj.status)

    @admin.action(description=_("Confirm selected bookings"))
    def confirm_bookings(self, request, queryset):
        updated = queryset.exclude(status=Booking.Status.CONFIRMED).update(
            status=Booking.Status.CONFIRMED
        )
        self.message_user(
            request,
            _("%(count)d booking(s) confirmed.") % {"count": updated},
            messages.SUCCESS,
        )

    @admin.action(description=_("Cancel selected bookings"))
    def cancel_bookings(self, request, queryset):
        updated = queryset.exclude(status=Booking.Status.CANCELLED).update(
            status=Booking.Status.CANCELLED
        )
        self.message_user(
            request,
            _("%(count)d booking(s) cancelled.") % {"count": updated},
            messages.WARNING,
        )

    @admin.action(description=_("Mark selected as completed"))
    def complete_bookings(self, request, queryset):
        updated = queryset.update(status=Booking.Status.COMPLETED)
        self.message_user(
            request,
            _("%(count)d booking(s) completed.") % {"count": updated},
            messages.SUCCESS,
        )


# ── dashboard context ────────────────────────────────────────────────────────


_original_each_context = admin.site.each_context


def _aida_each_context(request):
    ctx = _original_each_context(request)
    try:
        booking_counts = Booking.objects.aggregate(
            total=Count("id"),
            pending=Count("id", filter=Q(status=Booking.Status.PENDING)),
            confirmed=Count("id", filter=Q(status=Booking.Status.CONFIRMED)),
        )
        unread = ContactMessage.objects.filter(is_read=False).count()
        rooms_active = Room.objects.filter(is_active=True).count()
        ctx["aida_stats"] = {
            "pending_bookings": booking_counts["pending"],
            "confirmed_bookings": booking_counts["confirmed"],
            "total_bookings": booking_counts["total"],
            "unread_messages": unread,
            "active_rooms": rooms_active,
            "bookings_url": reverse("admin:hotel_booking_changelist"),
            "pending_url": reverse("admin:hotel_booking_changelist") + "?status__exact=pending",
            "messages_url": reverse("admin:hotel_contactmessage_changelist")
            + "?is_read__exact=0",
            "rooms_url": reverse("admin:hotel_room_changelist"),
        }
    except Exception:
        ctx["aida_stats"] = None
    return ctx


admin.site.each_context = _aida_each_context
admin.site.site_header = _("Aida Hotel")
admin.site.site_title = _("Aida Hotel CMS")
admin.site.index_title = _("Dashboard")
