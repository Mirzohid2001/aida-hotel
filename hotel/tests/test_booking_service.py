from datetime import date
from decimal import Decimal

from django.test import TestCase

from hotel.models import Booking, BookingRoom, Room, RoomType
from hotel.services.booking import BookingError, create_booking


class BookingServiceTests(TestCase):
    def setUp(self):
        self.room_type = RoomType.objects.create(name="Suite", slug="suite", base_price=Decimal("200.00"))
        self.room = Room.objects.create(room_type=self.room_type, number="301")

    def test_create_booking_success(self):
        booking = create_booking(
            guest_name="John Doe",
            email="john@example.com",
            phone="+998901234567",
            guests_count=2,
            check_in=date(2026, 10, 1),
            check_out=date(2026, 10, 3),
            room_type=self.room_type,
            room_ids=[self.room.pk],
        )
        self.assertTrue(booking.reference_code.startswith("AIDA-"))
        self.assertEqual(booking.estimated_total, Decimal("400.00"))
        self.assertEqual(booking.rooms.count(), 1)

    def test_create_booking_rejects_invalid_dates(self):
        with self.assertRaises(BookingError):
            create_booking(
                guest_name="John",
                email="j@example.com",
                phone="1",
                guests_count=1,
                check_in=date(2026, 10, 5),
                check_out=date(2026, 10, 5),
                room_type=self.room_type,
                room_ids=[self.room.pk],
            )

    def test_create_booking_rejects_unavailable_room(self):
        existing = Booking.objects.create(
            reference_code="AIDA-2026-0099",
            guest_name="Other",
            email="o@example.com",
            phone="1",
            check_in=date(2026, 10, 1),
            check_out=date(2026, 10, 5),
        )
        BookingRoom.objects.create(booking=existing, room=self.room, nightly_rate=Decimal("200.00"))
        with self.assertRaises(BookingError):
            create_booking(
                guest_name="John",
                email="j@example.com",
                phone="1",
                guests_count=1,
                check_in=date(2026, 10, 2),
                check_out=date(2026, 10, 4),
                room_type=self.room_type,
                room_ids=[self.room.pk],
            )
