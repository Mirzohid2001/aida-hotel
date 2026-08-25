from django.test import TestCase
from django.utils import timezone

from hotel.models import Booking
from hotel.services.references import generate_reference_code


class ReferenceCodeTests(TestCase):
    def test_generates_first_code_for_year(self):
        code = generate_reference_code()
        year = timezone.now().year
        self.assertEqual(code, f"AIDA-{year}-0001")

    def test_increments_sequence(self):
        year = timezone.now().year
        Booking.objects.create(
            reference_code=f"AIDA-{year}-0041",
            guest_name="A",
            email="a@example.com",
            phone="1",
            check_in="2026-01-01",
            check_out="2026-01-02",
        )
        self.assertEqual(generate_reference_code(), f"AIDA-{year}-0042")
