from io import BytesIO
from pathlib import Path

from django.core.files.base import ContentFile
from PIL import Image, ImageOps

DEFAULT_MAX_SIDE = 1920
DEFAULT_QUALITY = 80


def optimize_image_field(image_field, *, max_side=DEFAULT_MAX_SIDE, quality=DEFAULT_QUALITY):
    """
    Recompress an unsaved ImageField upload in-memory.
    Call only when field_file._committed is False (new upload).
    """
    if not image_field:
        return False

    file_obj = getattr(image_field, "file", None)
    if file_obj is None:
        return False

    try:
        file_obj.seek(0)
        img = Image.open(file_obj)
        img.load()
        img = ImageOps.exif_transpose(img)
    except Exception:
        try:
            file_obj.seek(0)
        except Exception:
            pass
        return False

    w, h = img.size
    longest = max(w, h)
    if longest > max_side:
        ratio = max_side / float(longest)
        img = img.resize(
            (max(1, int(w * ratio)), max(1, int(h * ratio))),
            Image.Resampling.LANCZOS,
        )

    has_alpha = img.mode in ("RGBA", "LA") or (
        img.mode == "P" and "transparency" in img.info
    )
    buf = BytesIO()
    original_name = Path(getattr(image_field, "name", None) or "image").stem[:80] or "image"

    if has_alpha:
        if img.mode != "RGBA":
            img = img.convert("RGBA")
        img.save(buf, format="PNG", optimize=True)
        ext = "png"
    else:
        if img.mode != "RGB":
            img = img.convert("RGB")
        img.save(
            buf,
            format="JPEG",
            quality=quality,
            optimize=True,
            progressive=True,
        )
        ext = "jpg"

    buf.seek(0)
    image_field.save(f"{original_name}.{ext}", ContentFile(buf.read()), save=False)
    return True
