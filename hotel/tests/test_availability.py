from datetime import date
from decimal import Decimal

from django.test import TestCase

from hotel.models import BlockedDate, Booking, BookingRoom, Room, RoomType
from hotel.services.availability import (
    dates_overlap,
    get_room_availability,
    is_room_available,
)


def attach_room(booking, room, rate=Decimal("100.00")):
    BookingRoom.objects.create(booking=booking, room=room, nightly_rate=rate)


class DatesOverlapTests(TestCase):
    def test_non_overlapping_ranges(self):
        self.assertFalse(dates_overlap(date(2026, 1, 1), date(2026, 1, 5), date(2026, 1, 5), date(2026, 1, 10)))

    def test_overlapping_ranges(self):
        self.assertTrue(dates_overlap(date(2026, 1, 1), date(2026, 1, 10), date(2026, 1, 5), date(2026, 1, 15)))

    def test_adjacent_ranges_do_not_overlap(self):
        self.assertFalse(dates_overlap(date(2026, 1, 1), date(2026, 1, 3), date(2026, 1, 3), date(2026, 1, 5)))

    def test_identical_ranges_overlap(self):
        self.assertTrue(dates_overlap(date(2026, 1, 1), date(2026, 1, 5), date(2026, 1, 1), date(2026, 1, 5)))


class RoomAvailabilityTests(TestCase):
    def setUp(self):
        self.room_type = RoomType.objects.create(name="Standard", slug="standard", base_price="100.00")
        self.room = Room.objects.create(room_type=self.room_type, number="101")

    def test_room_available_when_no_bookings(self):
        self.assertTrue(is_room_available(self.room, date(2026, 6, 1), date(2026, 6, 3)))

    def test_room_unavailable_when_booked(self):
        booking = Booking.objects.create(
            reference_code="AIDA-2026-0001",
            guest_name="Test Guest",
            email="test@example.com",
            phone="+998901234567",
            check_in=date(2026, 6, 1),
            check_out=date(2026, 6, 5),
        )
        attach_room(booking, self.room)
        self.assertFalse(is_room_available(self.room, date(2026, 6, 2), date(2026, 6, 4)))

    def test_back_to_back_bookings_allowed(self):
        booking = Booking.objects.create(
            reference_code="AIDA-2026-0002",
            guest_name="Test Guest",
            email="test@example.com",
            phone="+998901234567",
            check_in=date(2026, 6, 1),
            check_out=date(2026, 6, 3),
        )
        attach_room(booking, self.room)
        self.assertTrue(is_room_available(self.room, date(2026, 6, 3), date(2026, 6, 5)))

    def test_blocked_date_makes_room_unavailable(self):
        BlockedDate.objects.create(room=self.room, start_date=date(2026, 7, 1), end_date=date(2026, 7, 5))
        self.assertFalse(is_room_available(self.room, date(2026, 7, 2), date(2026, 7, 3)))

    def test_cancelled_booking_does_not_block(self):
        booking = Booking.objects.create(
            reference_code="AIDA-2026-0003",
            guest_name="Test Guest",
            email="test@example.com",
            phone="+998901234567",
            check_in=date(2026, 8, 1),
            check_out=date(2026, 8, 5),
            status=Booking.Status.CANCELLED,
        )
        attach_room(booking, self.room)
        self.assertTrue(is_room_available(self.room, date(2026, 8, 2), date(2026, 8, 4)))

    def test_get_room_availability_returns_statuses(self):
        room2 = Room.objects.create(room_type=self.room_type, number="102")
        booking = Booking.objects.create(
            reference_code="AIDA-2026-0004",
            guest_name="Guest",
            email="g@example.com",
            phone="+998901234567",
            check_in=date(2026, 9, 1),
            check_out=date(2026, 9, 3),
        )
        attach_room(booking, self.room)
        results = get_room_availability(self.room_type, date(2026, 9, 1), date(2026, 9, 3))
        by_number = {r["room"].number: r["available"] for r in results}
        self.assertFalse(by_number["101"])
        self.assertTrue(by_number["102"])
