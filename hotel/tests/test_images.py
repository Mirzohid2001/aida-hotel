from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from PIL import Image

from hotel.models import GalleryImage, RoomType


def _make_png(width=3000, height=2000) -> bytes:
    buf = BytesIO()
    # Noise so PNG stays large (solid color compresses too well)
    img = Image.effect_noise((width, height), 32).convert("RGB")
    img.save(buf, format="PNG")
    return buf.getvalue()


class ImageOptimizeTests(TestCase):
    def test_gallery_upload_is_resized_and_compressed(self):
        raw = _make_png()
        self.assertGreater(len(raw), 50_000)
        upload = SimpleUploadedFile("huge-room.png", raw, content_type="image/png")
        obj = GalleryImage(title="Test", image=upload)
        obj.save()
        obj.refresh_from_db()
        self.assertTrue(obj.image.name.endswith(".jpg"))
        self.assertLess(obj.image.size, len(raw) // 2)
        with obj.image.open("rb") as fh:
            img = Image.open(fh)
            self.assertLessEqual(max(img.size), 1920)

    def test_room_image_upload_optimized(self):
        rt = RoomType.objects.create(name="Deluxe", slug="deluxe-opt", base_price="100.00")
        upload = SimpleUploadedFile("room.png", _make_png(2500, 2500), content_type="image/png")
        from hotel.models import RoomImage

        img = RoomImage(room_type=rt, image=upload)
        img.save()
        with img.image.open("rb") as fh:
            opened = Image.open(fh)
            self.assertLessEqual(max(opened.size), 1920)
