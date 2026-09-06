from datetime import date, timedelta
from decimal import Decimal

from django.test import TestCase

from hotel.models import Booking, Room, RoomType, SiteSettings
from hotel.services.booking import create_booking
from hotel.utils.currency import Currency, format_money


class CurrencyTests(TestCase):
    def setUp(self):
        self.settings = SiteSettings.load()
        self.room_type = RoomType.objects.create(
            name="Deluxe", slug="deluxe-cur", base_price=Decimal("85.50")
        )
        self.room = Room.objects.create(room_type=self.room_type, number="501")

    def test_format_money_labels(self):
        self.assertEqual(format_money(Decimal("100000"), Currency.UZS), "100000 UZS")
        self.assertEqual(format_money(Decimal("85.5"), Currency.USD), "85.50 $")
        self.assertEqual(format_money(Decimal("70"), Currency.EUR), "70.00 €")

    def test_booking_snapshots_site_currency(self):
        self.settings.currency = Currency.EUR
        self.settings.save()
        check_in = date.today() + timedelta(days=14)
        check_out = check_in + timedelta(days=2)
        booking = create_booking(
            guest_name="Euro Guest",
            email="euro@example.com",
            phone="+998901111111",
            guests_count=1,
            check_in=check_in,
            check_out=check_out,
            room_type=self.room_type,
            room_ids=[self.room.pk],
        )
        self.assertEqual(booking.currency, Currency.EUR)
        self.assertIn("€", booking.format_total())

    def test_site_settings_accepts_eur(self):
        self.settings.currency = Currency.EUR
        self.settings.save()
        refreshed = SiteSettings.load()
        self.assertEqual(refreshed.currency, "EUR")
        self.assertEqual(refreshed.currency_label, "€")
