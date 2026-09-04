from django.conf import settings
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from django.utils import translation

from hotel.models import PolicyPage, RoomType


def _localized_url(lang: str, viewname: str, kwargs=None) -> str:
    with translation.override(lang):
        return reverse(viewname, kwargs=kwargs or {})


class StaticViewSitemap(Sitemap):
    priority = 0.9
    changefreq = "weekly"
    protocol = "https"

    def items(self):
        pages = ["hotel:home", "hotel:rooms", "hotel:book", "hotel:contact"]
        return [(lang, name) for lang, _ in settings.LANGUAGES for name in pages]

    def location(self, item):
        lang, name = item
        return _localized_url(lang, name)

    def priority(self, item):
        _lang, name = item
        return 1.0 if name == "hotel:home" else 0.8


class RoomTypeSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.75
    protocol = "https"

    def items(self):
        rooms = list(RoomType.objects.filter(is_active=True))
        return [(lang, room) for lang, _ in settings.LANGUAGES for room in rooms]

    def location(self, item):
        lang, room = item
        return _localized_url(lang, "hotel:room_detail", {"slug": room.slug})


class PolicyPageSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.35
    protocol = "https"

    def items(self):
        pages = list(PolicyPage.objects.filter(is_active=True))
        return [(lang, page) for lang, _ in settings.LANGUAGES for page in pages]

    def location(self, item):
        lang, page = item
        return _localized_url(lang, "hotel:policy", {"slug": page.slug})
