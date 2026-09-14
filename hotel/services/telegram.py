import html
import json
import logging
import urllib.error
import urllib.parse
import urllib.request

from django.utils.formats import date_format, number_format
from django.utils.translation import gettext as _

from hotel.models import Booking, SiteSettings

logger = logging.getLogger(__name__)

_SEP = "────────────────────"


def _e(value) -> str:
    return html.escape(str(value or ""), quote=False)


def _row(icon: str, label: str, value: str) -> str:
    return f"{icon} <b>{_e(label)}:</b> {value}"


def format_booking_notification(booking: Booking) -> str:
    site = SiteSettings.load()
    hotel_name = _e(site.site_name or "Aida Hotel")

    rooms = booking.booking_rooms.select_related("room", "room__room_type").all()
    room_parts = []
    for br in rooms:
        room_parts.append(f"<code>{_e(br.room.number)}</code> — {_e(br.room.room_type.name)}")
    room_labels = "\n".join(f"   • {part}" for part in room_parts) if room_parts else "—"

    nights = (booking.check_out - booking.check_in).days
    total = number_format(booking.estimated_total, force_grouping=True)
    currency = _e(booking.currency_label)
    phone = _e(booking.phone)
    email = _e(booking.email)
    status = _e(booking.get_status_display())

    lines = [
        f"🏨 <b>{hotel_name}</b>",
        f"✨ <b>{_('New booking')}</b>",
        _SEP,
        _row("🔖", _("Reference"), f"<code>{_e(booking.reference_code)}</code>"),
        _row("📌", _("Status"), f"<i>{status}</i>"),
        "",
        f"👤 <b>{_('Guest details')}</b>",
        _row("🧑", _("Guest"), _e(booking.guest_name)),
        _row("📞", _("Phone"), f'<a href="tel:{phone}">{phone}</a>'),
        _row("✉️", _("Email"), f'<a href="mailto:{email}">{email}</a>'),
        _row("👥", _("Guests"), _e(booking.guests_count)),
        "",
        f"📅 <b>{_('Stay')}</b>",
        _row("➡️", _("Check-in"), _e(date_format(booking.check_in, "DATE_FORMAT"))),
        _row("⬅️", _("Check-out"), _e(date_format(booking.check_out, "DATE_FORMAT"))),
        _row("🌙", _("Nights"), _e(nights)),
        "",
        f"🛏 <b>{_('Rooms')}</b>",
        room_labels,
        "",
        _SEP,
        f"💵 <b>{_('Total')}:</b> <code>{_e(total)} {currency}</code>",
    ]

    special = (booking.special_requests or "").strip()
    if special:
        lines.extend(
            [
                "",
                f"📝 <b>{_('Special requests')}</b>",
                f"<i>{_e(special)}</i>",
            ]
        )

    lines.extend(["", f"<i>{_('Open admin to confirm or update this booking.')}</i>"])
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
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:500]
        logger.warning("Failed to send Telegram notification: HTTP %s %s", exc.code, detail)
        return False
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
