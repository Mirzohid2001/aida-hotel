from datetime import datetime
import json

from django.conf import settings
from django.contrib import messages
from django.http import FileResponse, Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.translation import check_for_language, gettext as _
from django.views.decorators.http import require_GET, require_http_methods

from hotel.forms import BookingForm, ContactForm
from hotel.models import (
    AboutSection,
    Amenity,
    Booking,
    FAQ,
    GalleryImage,
    HeroSlide,
    NearbyPlace,
    PolicyPage,
    RoomType,
    SiteSettings,
    StatHighlight,
    Testimonial,
)
from hotel.seo import breadcrumb_json_ld, faq_json_ld, room_json_ld
from hotel.services.availability import get_room_availability
from hotel.services.booking import BookingError, create_booking
from hotel.services.pricing import calculate_booking_total, calculate_nights


def home(request):
    faqs = FAQ.objects.filter(is_active=True)
    faq_payload = faq_json_ld(faqs)
    context = {
        "hero_slides": HeroSlide.objects.filter(is_active=True),
        "about": AboutSection.load(),
        "amenities": Amenity.objects.filter(is_active=True),
        "gallery": GalleryImage.objects.filter(is_active=True)[:8],
        "testimonials": Testimonial.objects.filter(is_active=True)[:6],
        "faqs": faqs,
        "stats": StatHighlight.objects.filter(is_active=True),
        "nearby_places": NearbyPlace.objects.filter(is_active=True),
        "room_types": RoomType.objects.filter(is_active=True).prefetch_related("images", "rooms")[:3],
        "seo_faq_jsonld": (
            json.dumps(faq_payload, ensure_ascii=False, separators=(",", ":")) if faq_payload else ""
        ),
    }
    return render(request, "hotel/home.html", context)


def rooms(request):
    room_types = RoomType.objects.filter(is_active=True).prefetch_related("images", "rooms")
    return render(request, "hotel/rooms.html", {"room_types": room_types})


def room_detail(request, slug):
    room_type = get_object_or_404(
        RoomType.objects.prefetch_related("images", "rooms"),
        slug=slug,
        is_active=True,
    )
    related = (
        RoomType.objects.filter(is_active=True)
        .exclude(pk=room_type.pk)
        .prefetch_related("images")[:3]
    )
    site = SiteSettings.load()
    crumbs = breadcrumb_json_ld(
        request,
        [
            (_("Home"), reverse("hotel:home")),
            (_("Rooms"), reverse("hotel:rooms")),
            (room_type.name, request.path),
        ],
    )
    return render(
        request,
        "hotel/room_detail.html",
        {
            "room_type": room_type,
            "related_room_types": related,
            "seo_room_jsonld": json.dumps(
                room_json_ld(request, site, room_type),
                ensure_ascii=False,
                separators=(",", ":"),
            ),
            "seo_breadcrumb_jsonld": json.dumps(
                crumbs, ensure_ascii=False, separators=(",", ":")
            ),
        },
    )


@require_http_methods(["GET", "POST"])
def book(request):
    initial = {}
    room_type_slug = request.GET.get("room_type")
    if room_type_slug:
        rt = RoomType.objects.filter(slug=room_type_slug, is_active=True).first()
        if rt:
            initial["room_type"] = rt

    if request.method == "POST":
        form = BookingForm(request.POST)
        if form.is_valid():
            try:
                booking = create_booking(
                    guest_name=form.cleaned_data["guest_name"],
                    email=form.cleaned_data["email"],
                    phone=form.cleaned_data["phone"],
                    guests_count=form.cleaned_data["guests_count"],
                    check_in=form.cleaned_data["check_in"],
                    check_out=form.cleaned_data["check_out"],
                    room_type=form.cleaned_data["room_type"],
                    room_ids=form.get_selected_room_ids(),
                    special_requests=form.cleaned_data.get("special_requests", ""),
                )
                return redirect("hotel:booking_success", reference=booking.reference_code)
            except BookingError as exc:
                form.add_error(None, exc.message if hasattr(exc, "message") else str(exc))
    else:
        form = BookingForm(initial=initial)

    return render(request, "hotel/book.html", {"form": form})


@require_GET
def booking_availability(request):
    room_type_id = request.GET.get("room_type")
    check_in_raw = request.GET.get("check_in")
    check_out_raw = request.GET.get("check_out")

    if not all([room_type_id, check_in_raw, check_out_raw]):
        return render(request, "hotel/partials/room_grid.html", {"rooms": [], "error": _("Please select dates.")})

    room_type = get_object_or_404(RoomType, pk=room_type_id, is_active=True)
    try:
        check_in = datetime.strptime(check_in_raw, "%Y-%m-%d").date()
        check_out = datetime.strptime(check_out_raw, "%Y-%m-%d").date()
    except ValueError:
        return render(request, "hotel/partials/room_grid.html", {"rooms": [], "error": _("Invalid dates.")})

    if check_out <= check_in:
        return render(request, "hotel/partials/room_grid.html", {"rooms": [], "error": _("Check-out must be after check-in.")})

    rooms = get_room_availability(room_type, check_in, check_out)
    nights = calculate_nights(check_in, check_out)

    template = "hotel/partials/price_summary.html" if request.GET.get("partial") == "price" else "hotel/partials/room_grid.html"

    if template.endswith("price_summary.html"):
        selected_ids = [int(x) for x in request.GET.get("room_ids", "").split(",") if x.strip().isdigit()]
        selected_rooms = room_type.rooms.filter(pk__in=selected_ids, is_active=True)
        total = calculate_booking_total(selected_rooms, check_in, check_out) if selected_rooms else None
        return render(
            request,
            template,
            {
                "nights": nights,
                "total": total,
                "room_type": room_type,
                "selected_count": selected_rooms.count(),
            },
        )

    return render(
        request,
        template,
        {
            "rooms": rooms,
            "room_type": room_type,
            "check_in": check_in,
            "check_out": check_out,
            "nights": nights,
        },
    )


def booking_success(request, reference):
    booking = get_object_or_404(Booking, reference_code=reference)
    return render(request, "hotel/booking_success.html", {"booking": booking})


@require_http_methods(["GET", "POST"])
def contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, _("Thank you! We will get back to you soon."))
            return redirect("hotel:contact")
    else:
        form = ContactForm()
    return render(request, "hotel/contact.html", {"form": form})


def policy(request, slug):
    page = get_object_or_404(PolicyPage, slug=slug, is_active=True)
    return render(request, "hotel/policy.html", {"page": page})


from hotel.utils.i18n import localize_path


def switch_language(request, lang_code):
    """Switch language via GET link — fixes Django translate_url prefix bugs."""
    if not check_for_language(lang_code) or lang_code not in dict(settings.LANGUAGES):
        raise Http404()

    next_url = request.GET.get("next") or request.META.get("HTTP_REFERER") or "/"
    if not url_has_allowed_host_and_scheme(
        next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        next_url = "/"

    next_url = localize_path(next_url, lang_code)

    response = redirect(next_url)
    response.set_cookie(
        settings.LANGUAGE_COOKIE_NAME,
        lang_code,
        max_age=settings.LANGUAGE_COOKIE_AGE,
        path=settings.LANGUAGE_COOKIE_PATH,
        domain=settings.LANGUAGE_COOKIE_DOMAIN,
        secure=settings.LANGUAGE_COOKIE_SECURE,
        httponly=settings.LANGUAGE_COOKIE_HTTPONLY,
        samesite=settings.LANGUAGE_COOKIE_SAMESITE,
    )
    return response


def page_not_found(request, exception):
    return render(request, "404.html", status=404)


def server_error(request):
    return render(request, "500.html", status=500)


def favicon(request):
    path = settings.BASE_DIR / "static" / "favicon.ico"
    if not path.exists():
        path = settings.BASE_DIR / "static" / "images" / "brand" / "favicon.ico"
    if not path.exists():
        raise Http404()
    response = FileResponse(path.open("rb"), content_type="image/x-icon")
    response["Cache-Control"] = "public, max-age=0, must-revalidate"
    return response


def robots_txt(request):
    sitemap_url = request.build_absolute_uri("/sitemap.xml")
    lines = [
        "User-agent: *",
        "Allow: /",
        "Disallow: /admin/",
        "Disallow: /ru/admin/",
        "Disallow: /en/admin/",
        "Disallow: /book/success/",
        "Disallow: /ru/book/success/",
        "Disallow: /en/book/success/",
        f"Sitemap: {sitemap_url}",
    ]
    return HttpResponse("\n".join(lines) + "\n", content_type="text/plain")
