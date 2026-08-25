from datetime import date

from django.db.models import Q

from hotel.models import BlockedDate, Booking, Room, RoomType


def dates_overlap(start_a: date, end_a: date, start_b: date, end_b: date) -> bool:
    """Return True when two half-open date ranges [start, end) overlap."""
    return start_a < end_b and start_b < end_a


def _active_booking_filter(check_in: date, check_out: date) -> Q:
    return Q(
        bookings__status__in=[Booking.Status.PENDING, Booking.Status.CONFIRMED],
        bookings__check_in__lt=check_out,
        bookings__check_out__gt=check_in,
    )


def _blocked_filter(check_in: date, check_out: date) -> Q:
    return Q(
        blocked_dates__start_date__lt=check_out,
        blocked_dates__end_date__gt=check_in,
    )


def is_room_available(room: Room, check_in: date, check_out: date) -> bool:
    if not room.is_active:
        return False
    if check_out <= check_in:
        return False

    if BlockedDate.objects.filter(
        room=room,
        start_date__lt=check_out,
        end_date__gt=check_in,
    ).exists():
        return False

    return not Booking.objects.filter(
        rooms=room,
        status__in=[Booking.Status.PENDING, Booking.Status.CONFIRMED],
        check_in__lt=check_out,
        check_out__gt=check_in,
    ).exists()


def get_room_availability(room_type: RoomType, check_in: date, check_out: date) -> list[dict]:
    """Return availability info for each active room of the given type."""
    rooms = (
        Room.objects.filter(room_type=room_type, is_active=True)
        .select_related("room_type")
        .order_by("floor", "number")
    )
    results = []
    for room in rooms:
        available = is_room_available(room, check_in, check_out)
        results.append(
            {
                "room": room,
                "available": available,
                "status_label": "available" if available else "occupied",
            }
        )
    return results


def get_available_rooms(room_type: RoomType, check_in: date, check_out: date):
    """Return queryset of rooms available for the date range."""
    unavailable_ids = set()

    for room in Room.objects.filter(room_type=room_type, is_active=True):
        if not is_room_available(room, check_in, check_out):
            unavailable_ids.add(room.pk)

    return Room.objects.filter(room_type=room_type, is_active=True).exclude(pk__in=unavailable_ids)
