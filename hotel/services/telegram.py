import json
import logging
import urllib.error
import urllib.parse
import urllib.request

from django.utils.formats import date_format, number_format
from django.utils.translation import gettext as _

from hotel.models import Booking, SiteSettings

logger = logging.getLogger(__name__)


def format_booking_notification(booking: Booking) -> str:
    rooms = booking.booking_rooms.select_related("room", "room__room_type").all()
    room_labels = ", ".join(f"{br.room.number} ({br.room.room_type.name})" for br in rooms)
    nights = (booking.check_out - booking.check_in).days
    total = number_format(booking.estimated_total, force_grouping=True)
    currency = booking.currency_label

    lines = [
        f"<b>{_('New booking')}</b>",
        "",
        f"<b>{_('Reference')}:</b> {booking.reference_code}",
        f"<b>{_('Guest')}:</b> {booking.guest_name}",
        f"<b>{_('Phone')}:</b> {booking.phone}",
        f"<b>{_('Email')}:</b> {booking.email}",
        f"<b>{_('Guests')}:</b> {booking.guests_count}",
        f"<b>{_('Check-in')}:</b> {date_format(booking.check_in, 'DATE_FORMAT')}",
        f"<b>{_('Check-out')}:</b> {date_format(booking.check_out, 'DATE_FORMAT')}",
        f"<b>{_('Nights')}:</b> {nights}",
        f"<b>{_('Rooms')}:</b> {room_labels or '—'}",
        f"<b>{_('Total')}:</b> {total} {currency}",
    ]

    if booking.special_requests.strip():
        lines.extend(["", f"<b>{_('Special requests')}:</b> {booking.special_requests.strip()}"])

    return "\n".join(lines)


def send_telegram_message(*, bot_token: str, chat_id: str, text: str) -> bool:
    if not bot_token or not chat_id:
        return False

    payload = urllib.parse.urlencode(
        {
            "chat_id": chat_id.strip(),
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": "true",
        }
    ).encode("utf-8")
    url = f"https://api.telegram.org/bot{bot_token.strip()}/sendMessage"
    request = urllib.request.Request(url, data=payload, method="POST")

    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            body = json.loads(response.read().decode("utf-8"))
            if not body.get("ok"):
                logger.warning("Telegram API error: %s", body)
                return False
            return True
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        logger.warning("Failed to send Telegram notification: %s", exc)
        return False


def notify_booking_created(booking: Booking) -> bool:
    settings = SiteSettings.load()
    if not settings.telegram_notifications_enabled:
        return False
    if not settings.telegram_bot_token or not settings.telegram_chat_id:
        logger.info("Telegram notifications enabled but token or chat ID is missing.")
        return False

    message = format_booking_notification(booking)
    return send_telegram_message(
        bot_token=settings.telegram_bot_token,
        chat_id=settings.telegram_chat_id,
        text=message,
    )
