from datetime import date, timedelta
from decimal import Decimal

from hotel.models import Room, RoomType, SeasonalPrice


def calculate_nights(check_in: date, check_out: date) -> int:
    if check_out <= check_in:
        return 0
    return (check_out - check_in).days


def get_nightly_rate(room_type: RoomType, night: date) -> Decimal:
    seasonal = (
        SeasonalPrice.objects.filter(
            room_type=room_type,
            start_date__lte=night,
            end_date__gt=night,
        )
        .order_by("-start_date")
        .first()
    )
    if seasonal:
        return seasonal.price
    return room_type.base_price


def calculate_room_total(room: Room, check_in: date, check_out: date) -> Decimal:
    total = Decimal("0.00")
    night = check_in
    while night < check_out:
        total += get_nightly_rate(room.room_type, night)
        night += timedelta(days=1)
    return total


def calculate_booking_total(rooms, check_in: date, check_out: date) -> Decimal:
    total = Decimal("0.00")
    for room in rooms:
        total += calculate_room_total(room, check_in, check_out)
    return total.quantize(Decimal("0.01"))
