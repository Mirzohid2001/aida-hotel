from django.test import TestCase

from hotel.utils.i18n import localize_path


class LocalizePathTests(TestCase):
    def test_root_to_russian(self):
        self.assertEqual(localize_path("/", "ru"), "/ru/")

    def test_root_to_uzbek(self):
        self.assertEqual(localize_path("/", "uz"), "/")

    def test_russian_to_uzbek(self):
        self.assertEqual(localize_path("/ru/", "uz"), "/")
        self.assertEqual(localize_path("/ru/book/", "uz"), "/book/")

    def test_russian_to_english(self):
        self.assertEqual(localize_path("/ru/book/", "en"), "/en/book/")

    def test_english_to_russian(self):
        self.assertEqual(localize_path("/en/rooms/", "ru"), "/ru/rooms/")

    def test_uzbek_to_english(self):
        self.assertEqual(localize_path("/book/", "en"), "/en/book/")
