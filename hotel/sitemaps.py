from django.conf import settings
from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from hotel.models import PolicyPage, RoomType

_LANGUAGES = [code for code, _ in settings.LANGUAGES]


class StaticViewSitemap(Sitemap):
    changefreq = "weekly"
    protocol = "https"
    i18n = True
    languages = _LANGUAGES
    alternates = True
    x_default = True

    def items(self):
        return ["hotel:home", "hotel:rooms", "hotel:book", "hotel:contact"]

    def location(self, item):
        return reverse(item)

    def priority(self, item):
        return 1.0 if item == "hotel:home" else 0.8


class RoomTypeSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.75
    protocol = "https"
    i18n = True
    languages = _LANGUAGES
    alternates = True
    x_default = True

    def items(self):
        return RoomType.objects.filter(is_active=True)

    def location(self, item):
        return reverse("hotel:room_detail", kwargs={"slug": item.slug})


class PolicyPageSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.35
    protocol = "https"
    i18n = True
    languages = _LANGUAGES
    alternates = True
    x_default = True

    def items(self):
        return PolicyPage.objects.filter(is_active=True)

    def location(self, item):
        return reverse("hotel:policy", kwargs={"slug": item.slug})
