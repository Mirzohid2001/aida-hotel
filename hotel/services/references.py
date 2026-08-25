from django.utils import timezone

from hotel.models import Booking


def generate_reference_code() -> str:
    year = timezone.now().year
    prefix = f"AIDA-{year}-"
    last = (
        Booking.objects.filter(reference_code__startswith=prefix)
        .order_by("-reference_code")
        .values_list("reference_code", flat=True)
        .first()
    )
    if last:
        try:
            seq = int(last.rsplit("-", 1)[-1]) + 1
        except (ValueError, IndexError):
            seq = 1
    else:
        seq = 1
    return f"{prefix}{seq:04d}"
