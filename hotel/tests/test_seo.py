from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from hotel.models import FAQ, RoomType, SiteSettings


class SeoTests(TestCase):
    def setUp(self):
        SiteSettings.load()
        self.room_type = RoomType.objects.create(
            name="Deluxe",
            slug="deluxe",
            base_price=Decimal("250000.00"),
            description="Quiet deluxe room in Bukhara.",
        )
        FAQ.objects.create(
            question="Where is Aida Hotel?",
            answer="In the historic center of Bukhara.",
            is_active=True,
        )

    def test_home_has_hotel_and_faq_jsonld(self):
        response = self.client.get(reverse("hotel:home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'application/ld+json')
        self.assertContains(response, '"@type":"Hotel"')
        self.assertContains(response, '"@type":"FAQPage"')
        self.assertContains(response, "Bukhara")
        self.assertContains(response, 'rel="canonical"')
        self.assertContains(response, 'hreflang="uz"')
        self.assertContains(response, 'hreflang="ru"')
        self.assertContains(response, 'hreflang="en"')

    def test_room_detail_has_room_jsonld(self):
        response = self.client.get(
            reverse("hotel:room_detail", kwargs={"slug": "deluxe"})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '"@type":"HotelRoom"')
        self.assertContains(response, '"@type":"BreadcrumbList"')
        self.assertContains(response, "Deluxe")

    def test_robots_and_sitemap(self):
        robots = self.client.get("/robots.txt")
        self.assertEqual(robots.status_code, 200)
        self.assertIn(b"Sitemap:", robots.content)
        self.assertIn(b"Disallow: /admin/", robots.content)

        sitemap = self.client.get("/sitemap.xml")
        self.assertEqual(sitemap.status_code, 200)
        self.assertContains(sitemap, "/rooms/")
        self.assertContains(sitemap, "/rooms/deluxe/")
        self.assertContains(sitemap, "/ru/")
        self.assertContains(sitemap, "/en/")
        self.assertContains(sitemap, 'rel="alternate"')
        self.assertContains(sitemap, "xhtml:link")
        self.assertContains(sitemap, 'hreflang="x-default"')

    def test_booking_success_is_noindex(self):
        from datetime import date

        from hotel.models import Booking

        booking = Booking.objects.create(
            reference_code="AIDA-2030-0099",
            guest_name="Test Guest",
            email="t@example.com",
            phone="+998901112233",
            guests_count=1,
            check_in=date(2030, 1, 10),
            check_out=date(2030, 1, 12),
            estimated_total=Decimal("500000.00"),
        )
        response = self.client.get(
            reverse("hotel:booking_success", kwargs={"reference": booking.reference_code})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'content="noindex, nofollow"')
