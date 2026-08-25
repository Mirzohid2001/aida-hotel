from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class HotelConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "hotel"
    verbose_name = _("Aida Hotel CMS")

    def ready(self):
        from . import translation  # noqa: F401
