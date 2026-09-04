from django.conf import settings
from django.utils.translation import get_language

from hotel.utils.i18n import localize_path, strip_language_prefix


def absolute_uri(request, path: str) -> str:
    return request.build_absolute_uri(path)


def seo_alternates(request) -> dict[str, str]:
    """Absolute URLs for the same page in each language."""
    clean = strip_language_prefix(request.path)
    return {
        code: absolute_uri(request, localize_path(clean, code))
        for code, _ in settings.LANGUAGES
    }


def default_meta_description() -> str:
    """Fallback when SiteSettings.meta_description is empty."""
    from django.utils.translation import gettext as _

    return _(
        "Aida Hotel Bukhara — boutique hotel in the historic center of Bukhara. "
        "Comfortable rooms, courtyard atmosphere, and easy booking."
    )


def hotel_json_ld(request, site) -> dict:
    """schema.org Hotel / LodgingBusiness payload."""
    url = absolute_uri(request, "/")
    data = {
        "@context": "https://schema.org",
        "@type": "Hotel",
        "name": site.site_name or "Aida Hotel",
        "url": url,
        "description": (site.meta_description or default_meta_description()).strip(),
        "address": {
            "@type": "PostalAddress",
            "addressLocality": "Bukhara",
            "addressRegion": "Bukhara",
            "addressCountry": "UZ",
        },
    }
    if site.address:
        data["address"]["streetAddress"] = site.address
    if site.phone:
        data["telephone"] = site.phone
    if site.email:
        data["email"] = site.email
    if site.map_latitude is not None and site.map_longitude is not None:
        data["geo"] = {
            "@type": "GeoCoordinates",
            "latitude": float(site.map_latitude),
            "longitude": float(site.map_longitude),
        }
    logo = site.og_image or site.logo
    if logo:
        data["image"] = absolute_uri(request, logo.url)
        data["logo"] = absolute_uri(request, logo.url)
    if site.check_in_time:
        data["checkinTime"] = site.check_in_time
    if site.check_out_time:
        data["checkoutTime"] = site.check_out_time
    same_as = [u for u in (site.instagram_url, site.facebook_url, site.telegram_url) if u]
    if same_as:
        data["sameAs"] = same_as
    data["priceRange"] = site.currency_label
    return data


def room_json_ld(request, site, room_type) -> dict:
    """schema.org HotelRoom + Offer for a room type page."""
    from django.urls import reverse

    url = request.build_absolute_uri()
    primary = room_type.images.filter(is_primary=True).first() or room_type.images.first()
    data = {
        "@context": "https://schema.org",
        "@type": "HotelRoom",
        "name": room_type.name,
        "description": (room_type.description or room_type.name)[:500],
        "url": url,
        "occupancy": {
            "@type": "QuantitativeValue",
            "maxValue": room_type.capacity,
        },
        "offers": {
            "@type": "Offer",
            "priceCurrency": site.currency if site.currency else "UZS",
            "price": str(room_type.base_price),
            "url": absolute_uri(request, reverse("hotel:book")),
            "availability": "https://schema.org/InStock",
        },
        "containedInPlace": {
            "@type": "Hotel",
            "name": site.site_name or "Aida Hotel",
            "address": {
                "@type": "PostalAddress",
                "addressLocality": "Bukhara",
                "addressCountry": "UZ",
            },
        },
    }
    if room_type.size_sqm:
        data["floorSize"] = {
            "@type": "QuantitativeValue",
            "value": room_type.size_sqm,
            "unitCode": "MTK",
        }
    if primary and primary.image:
        data["image"] = absolute_uri(request, primary.image.url)
    return data


def faq_json_ld(faqs) -> dict | None:
    items = list(faqs)[:12]
    if not items:
        return None
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": faq.question,
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": faq.answer,
                },
            }
            for faq in items
        ],
    }


def breadcrumb_json_ld(request, crumbs: list[tuple[str, str]]) -> dict:
    """crumbs: list of (name, path_or_absolute_url)."""
    elements = []
    for i, (name, href) in enumerate(crumbs, start=1):
        item = href if href.startswith("http") else absolute_uri(request, href)
        elements.append(
            {
                "@type": "ListItem",
                "position": i,
                "name": name,
                "item": item,
            }
        )
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": elements,
    }


def current_og_locale() -> str:
    lang = get_language() or settings.LANGUAGE_CODE
    return {
        "uz": "uz_UZ",
        "ru": "ru_RU",
        "en": "en_US",
    }.get(lang, "uz_UZ")
