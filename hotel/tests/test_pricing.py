from datetime import date
from decimal import Decimal

from django.test import TestCase

from hotel.models import Room, RoomType, SeasonalPrice
from hotel.services.pricing import (
    calculate_booking_total,
    calculate_nights,
    get_nightly_rate,
)


class PricingTests(TestCase):
    def setUp(self):
        self.room_type = RoomType.objects.create(name="Deluxe", slug="deluxe", base_price=Decimal("120.00"))
        self.room = Room.objects.create(room_type=self.room_type, number="201")

    def test_calculate_nights(self):
        self.assertEqual(calculate_nights(date(2026, 1, 1), date(2026, 1, 4)), 3)
        self.assertEqual(calculate_nights(date(2026, 1, 1), date(2026, 1, 1)), 0)

    def test_base_price_used(self):
        self.assertEqual(get_nightly_rate(self.room_type, date(2026, 5, 10)), Decimal("120.00"))

    def test_seasonal_price_overrides_base(self):
        SeasonalPrice.objects.create(
            room_type=self.room_type,
            start_date=date(2026, 6, 1),
            end_date=date(2026, 6, 30),
            price=Decimal("180.00"),
        )
        self.assertEqual(get_nightly_rate(self.room_type, date(2026, 6, 15)), Decimal("180.00"))
        self.assertEqual(get_nightly_rate(self.room_type, date(2026, 7, 1)), Decimal("120.00"))

    def test_calculate_booking_total_single_room(self):
        total = calculate_booking_total([self.room], date(2026, 5, 1), date(2026, 5, 4))
        self.assertEqual(total, Decimal("360.00"))

    def test_calculate_booking_total_with_seasonal_mix(self):
        SeasonalPrice.objects.create(
            room_type=self.room_type,
            start_date=date(2026, 5, 2),
            end_date=date(2026, 5, 10),
            price=Decimal("150.00"),
        )
        total = calculate_booking_total([self.room], date(2026, 5, 1), date(2026, 5, 4))
        self.assertEqual(total, Decimal("420.00"))
