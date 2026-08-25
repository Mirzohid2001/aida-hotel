from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from hotel.models import PolicyPage, RoomType


class StaticViewSitemap(Sitemap):
    priority = 0.8
    changefreq = "weekly"

    def items(self):
        return ["hotel:home", "hotel:rooms", "hotel:book", "hotel:contact"]

    def location(self, item):
        return reverse(item)


class RoomTypeSitemap(Sitemap):
    priority = 0.7
    changefreq = "weekly"

    def items(self):
        return RoomType.objects.filter(is_active=True)

    def location(self, obj):
        return reverse("hotel:room_detail", kwargs={"slug": obj.slug})


class PolicyPageSitemap(Sitemap):
    priority = 0.4
    changefreq = "monthly"

    def items(self):
        return PolicyPage.objects.filter(is_active=True)

    def location(self, obj):
        return reverse("hotel:policy", kwargs={"slug": obj.slug})
