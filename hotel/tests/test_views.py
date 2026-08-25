from datetime import date, timedelta
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from hotel.models import AboutSection, PolicyPage, Room, RoomType, SiteSettings


class ViewTests(TestCase):
    def setUp(self):
        SiteSettings.load()
        AboutSection.load()
        self.room_type = RoomType.objects.create(name="Standard", slug="standard", base_price=Decimal("100.00"))
        self.room = Room.objects.create(room_type=self.room_type, number="101")
        PolicyPage.objects.create(title="Privacy", slug="privacy", content="Policy text")

    def test_home_page(self):
        response = self.client.get(reverse("hotel:home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Aida")

    def test_rooms_page(self):
        response = self.client.get(reverse("hotel:rooms"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Standard")

    def test_room_detail_page(self):
        response = self.client.get(reverse("hotel:room_detail", kwargs={"slug": "standard"}))
        self.assertEqual(response.status_code, 200)

    def test_book_page_get(self):
        response = self.client.get(reverse("hotel:book"))
        self.assertEqual(response.status_code, 200)

    def test_booking_availability_htmx(self):
        check_in = date.today() + timedelta(days=10)
        check_out = check_in + timedelta(days=2)
        response = self.client.get(
            reverse("hotel:booking_availability"),
            {
                "room_type": self.room_type.pk,
                "check_in": check_in.isoformat(),
                "check_out": check_out.isoformat(),
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "101")

    def test_contact_page(self):
        response = self.client.get(reverse("hotel:contact"))
        self.assertEqual(response.status_code, 200)

    def test_policy_page(self):
        response = self.client.get(reverse("hotel:policy", kwargs={"slug": "privacy"}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Policy text")

    def test_booking_flow(self):
        check_in = date.today() + timedelta(days=20)
        check_out = check_in + timedelta(days=2)
        response = self.client.post(
            reverse("hotel:book"),
            {
                "room_type": self.room_type.pk,
                "check_in": check_in.isoformat(),
                "check_out": check_out.isoformat(),
                "guest_name": "Jane Doe",
                "email": "jane@example.com",
                "phone": "+998901234567",
                "guests_count": 2,
                "room_ids": str(self.room.pk),
                "website": "",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn("/book/success/AIDA-", response.url)

    def test_switch_language_to_russian(self):
        response = self.client.get(
            reverse("switch_language", kwargs={"lang_code": "ru"}),
            {"next": "/book/"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/ru/book/")
        self.assertEqual(response.cookies["django_language"].value, "ru")

    def test_switch_language_ru_to_uz(self):
        response = self.client.get(
            reverse("switch_language", kwargs={"lang_code": "uz"}),
            {"next": "/ru/book/"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/book/")
        self.assertEqual(response.cookies["django_language"].value, "uz")

    def test_switch_language_ru_to_en(self):
        response = self.client.get(
            reverse("switch_language", kwargs={"lang_code": "en"}),
            {"next": "/ru/rooms/"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/en/rooms/")

    def test_switch_language_invalid_code(self):
        response = self.client.get(reverse("switch_language", kwargs={"lang_code": "fr"}))
        self.assertEqual(response.status_code, 404)
