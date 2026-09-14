from datetime import date
from decimal import Decimal
from unittest.mock import MagicMock, patch

from django.test import TestCase

from hotel.models import Booking, BookingRoom, Room, RoomType, SiteSettings
from hotel.services.booking import create_booking
from hotel.services.telegram import format_booking_notification, notify_booking_created, send_telegram_message


class TelegramServiceTests(TestCase):
    def setUp(self):
        self.room_type = RoomType.objects.create(name="Suite", slug="suite", base_price=Decimal("200.00"))
        self.room = Room.objects.create(room_type=self.room_type, number="301")
        self.settings = SiteSettings.load()
        self.settings.telegram_notifications_enabled = True
        self.settings.telegram_bot_token = "123456:TEST_TOKEN"
        self.settings.telegram_chat_id = "-1001234567890"
        self.settings.save()

    def test_format_booking_notification_includes_key_fields(self):
        booking = Booking.objects.create(
            reference_code="AIDA-2026-0001",
            guest_name="Ali Valiyev",
            email="ali@example.com",
            phone="+998901112233",
            guests_count=2,
            check_in=date(2026, 10, 1),
            check_out=date(2026, 10, 3),
            special_requests="Late check-in",
            estimated_total=Decimal("400.00"),
        )
        BookingRoom.objects.create(booking=booking, room=self.room, nightly_rate=Decimal("200.00"))

        message = format_booking_notification(booking)

        self.assertIn("AIDA-2026-0001", message)
        self.assertIn("Ali Valiyev", message)
        self.assertIn("301", message)
        self.assertIn("Late check-in", message)
        self.assertIn("<code>", message)
        self.assertIn("tel:+998901112233", message)
        self.assertIn("mailto:ali@example.com", message)

    @patch("hotel.services.telegram.urllib.request.urlopen")
    def test_send_telegram_message_success(self, mock_urlopen):
        mock_response = MagicMock()
        mock_response.read.return_value = b'{"ok": true}'
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        sent = send_telegram_message(
            bot_token="123456:TEST_TOKEN",
            chat_id="-1001234567890",
            text="Hello",
        )

        self.assertTrue(sent)
        mock_urlopen.assert_called_once()

    @patch("hotel.services.booking.notify_booking_created")
    def test_create_booking_triggers_telegram_notification(self, mock_notify):
        create_booking(
            guest_name="John Doe",
            email="john@example.com",
            phone="+998901234567",
            guests_count=2,
            check_in=date(2026, 10, 1),
            check_out=date(2026, 10, 3),
            room_type=self.room_type,
            room_ids=[self.room.pk],
        )
        mock_notify.assert_called_once()

    @patch("hotel.services.telegram.send_telegram_message")
    def test_notify_booking_created_skips_when_disabled(self, mock_send):
        self.settings.telegram_notifications_enabled = False
        self.settings.save()

        booking = Booking.objects.create(
            reference_code="AIDA-2026-0002",
            guest_name="Test",
            email="t@example.com",
            phone="1",
            check_in=date(2026, 10, 1),
            check_out=date(2026, 10, 2),
        )

        self.assertFalse(notify_booking_created(booking))
        mock_send.assert_not_called()

    @patch("hotel.services.telegram.send_telegram_message", return_value=True)
    def test_notify_booking_created_sends_when_enabled(self, mock_send):
        booking = Booking.objects.create(
            reference_code="AIDA-2026-0003",
            guest_name="Test",
            email="t@example.com",
            phone="1",
            check_in=date(2026, 10, 1),
            check_out=date(2026, 10, 2),
        )

        self.assertTrue(notify_booking_created(booking))
        mock_send.assert_called_once()
