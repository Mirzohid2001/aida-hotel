from datetime import date
import json

from django.db.models import Q

from hotel.models import PolicyPage, Promotion, SiteSettings
from hotel.seo import (
    current_og_locale,
    default_meta_description,
    hotel_json_ld,
    seo_alternates,
)


def site_settings(request):
    return {"site_settings": SiteSettings.load()}


def active_promotion(request):
    today = date.today()
    promo = (
        Promotion.objects.filter(is_active=True)
        .filter(Q(starts_at__isnull=True) | Q(starts_at__lte=today))
        .filter(Q(ends_at__isnull=True) | Q(ends_at__gte=today))
        .order_by("-starts_at", "id")
        .first()
    )
    return {"active_promotion": promo}


def policy_pages(request):
    return {
        "policy_pages": PolicyPage.objects.filter(is_active=True).order_by("title"),
    }


def seo(request):
    site = SiteSettings.load()
    alternates = seo_alternates(request)
    description = (site.meta_description or "").strip() or default_meta_description()
    return {
        "seo_canonical": request.build_absolute_uri(request.path),
        "seo_alternates": alternates,
        "seo_x_default": alternates.get("uz") or request.build_absolute_uri("/"),
        "seo_description": description,
        "seo_og_locale": current_og_locale(),
        "seo_hotel_jsonld": json.dumps(
            hotel_json_ld(request, site), ensure_ascii=False, separators=(",", ":")
        ),
    }
