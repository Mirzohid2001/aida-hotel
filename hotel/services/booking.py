from datetime import date
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils.translation import gettext_lazy as _

from hotel.models import Booking, BookingRoom, Room, RoomType, SiteSettings
from hotel.services.availability import get_available_rooms, is_room_available
from hotel.services.pricing import calculate_booking_total, calculate_nights, get_nightly_rate
from hotel.services.references import generate_reference_code
from hotel.services.telegram import notify_booking_created


class BookingError(ValidationError):
    pass


def validate_booking_dates(check_in: date, check_out: date) -> None:
    if check_out <= check_in:
        raise BookingError(_("Check-out must be after check-in."))
    if calculate_nights(check_in, check_out) < 1:
        raise BookingError(_("Stay must be at least one night."))


def validate_room_selection(room_ids: list[int], room_type: RoomType, check_in: date, check_out: date) -> list[Room]:
    if not room_ids:
        raise BookingError(_("Please select at least one room."))

    rooms = list(Room.objects.filter(pk__in=room_ids, room_type=room_type, is_active=True))
    if len(rooms) != len(set(room_ids)):
        raise BookingError(_("One or more selected rooms are invalid."))

    for room in rooms:
        if not is_room_available(room, check_in, check_out):
            raise BookingError(_("Room %(room)s is no longer available.") % {"room": room.number})

    return rooms


@transaction.atomic
def create_booking(
    *,
    guest_name: str,
    email: str,
    phone: str,
    guests_count: int,
    check_in: date,
    check_out: date,
    room_type: RoomType,
    room_ids: list[int],
    special_requests: str = "",
) -> Booking:
    validate_booking_dates(check_in, check_out)
    rooms = validate_room_selection(room_ids, room_type, check_in, check_out)

    total = calculate_booking_total(rooms, check_in, check_out)

    booking = Booking.objects.create(
        reference_code=generate_reference_code(),
        guest_name=guest_name,
        email=email,
        phone=phone,
        guests_count=guests_count,
        check_in=check_in,
        check_out=check_out,
        special_requests=special_requests,
        estimated_total=total,
        currency=SiteSettings.load().currency,
        status=Booking.Status.PENDING,
    )

    for room in rooms:
        nightly = get_nightly_rate(room.room_type, check_in)
        BookingRoom.objects.create(booking=booking, room=room, nightly_rate=nightly)

    notify_booking_created(booking)

    return booking
