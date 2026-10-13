import time
from decimal import Decimal

from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse

from hotel.models import Testimonial
from hotel.forms import ReviewForm


class ReviewSubmissionTests(TestCase):
    def setUp(self):
        cache.clear()
        Testimonial.objects.create(
            guest_name="Published Guest",
            content="Wonderful stay in Bukhara courtyard hotel.",
            rating=5,
            is_active=True,
            source=Testimonial.Source.ADMIN,
        )

    def test_home_shows_carousel_and_form(self):
        response = self.client.get(reverse("hotel:home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "data-reviews-carousel")
        self.assertContains(response, "Published Guest")
        self.assertContains(response, 'action="/reviews/submit/"')

    def test_submit_review_creates_unpublished(self):
        response = self.client.post(
            reverse("hotel:submit_review"),
            {
                "guest_name": "New Guest",
                "email": "guest@example.com",
                "rating": 5,
                "content": "Beautiful rooms and kind staff in Bukhara.",
                "website": "",
                "form_ts": str(int(time.time()) - 5),
            },
        )
        self.assertEqual(response.status_code, 302)
        review = Testimonial.objects.get(guest_name="New Guest")
        self.assertFalse(review.is_active)
        self.assertEqual(review.source, Testimonial.Source.GUEST)

    def test_honeypot_blocks_bots(self):
        response = self.client.post(
            reverse("hotel:submit_review"),
            {
                "guest_name": "Bot",
                "email": "bot@example.com",
                "rating": 5,
                "content": "Spam review content here for bots.",
                "website": "http://spam.test",
                "form_ts": str(int(time.time()) - 5),
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertFalse(Testimonial.objects.filter(guest_name="Bot").exists())

    def test_fast_submit_blocked(self):
        form = ReviewForm(
            data={
                "guest_name": "Speedy",
                "email": "s@example.com",
                "rating": 4,
                "content": "Too fast submission should be rejected now.",
                "website": "",
                "form_ts": str(int(time.time())),
            },
            client_ip="1.2.3.4",
        )
        self.assertFalse(form.is_valid())

    def test_links_in_review_blocked(self):
        form = ReviewForm(
            data={
                "guest_name": "Linker",
                "email": "l@example.com",
                "rating": 5,
                "content": "Visit https://spam.example for deals please.",
                "website": "",
                "form_ts": str(int(time.time()) - 5),
            },
            client_ip="1.2.3.5",
        )
        self.assertFalse(form.is_valid())

    def test_unpublished_not_on_home(self):
        Testimonial.objects.create(
            guest_name="Hidden",
            content="Should not appear until approved by admin staff.",
            rating=5,
            is_active=False,
            source=Testimonial.Source.GUEST,
        )
        response = self.client.get(reverse("hotel:home"))
        self.assertNotContains(response, "Hidden")
