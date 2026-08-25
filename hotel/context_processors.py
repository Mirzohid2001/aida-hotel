from datetime import date

from django.db.models import Q

from hotel.models import PolicyPage, Promotion, SiteSettings


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
