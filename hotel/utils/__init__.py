from hotel.utils.images import optimize_image_field


class OptimizeImagesMixin:
    """Compress/resize new ImageField uploads before they hit disk."""

    image_optimize_fields: tuple[str, ...] = ()
    image_max_side = 1920
    image_quality = 80

    def save(self, *args, **kwargs):
        for field_name in self.image_optimize_fields:
            field = getattr(self, field_name, None)
            if field and getattr(field, "_committed", True) is False:
                optimize_image_field(
                    field,
                    max_side=self.image_max_side,
                    quality=self.image_quality,
                )
        return super().save(*args, **kwargs)
