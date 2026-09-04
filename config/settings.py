from pathlib import Path

import environ
from django.utils.translation import gettext_lazy as _

BASE_DIR = Path(__file__).resolve().parent.parent

import os

env = environ.Env(
    DEBUG=(bool, True),
    SECRET_KEY=(str, "django-insecure-dev-key-change-in-production"),
    ALLOWED_HOSTS=(list, ["localhost", "127.0.0.1"]),
)

environ.Env.read_env(BASE_DIR / ".env")

SECRET_KEY = env("SECRET_KEY")
DEBUG = env("DEBUG")
ALLOWED_HOSTS = list(env("ALLOWED_HOSTS"))

# ngrok / tunnel URLs (development)
if DEBUG:
    ALLOWED_HOSTS += [
        ".ngrok-free.app",
        ".ngrok.io",
        ".ngrok.app",
    ]

CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[])
if DEBUG:
    CSRF_TRUSTED_ORIGINS += [
        "https://.ngrok-free.app",
        "https://.ngrok.io",
        "https://.ngrok.app",
    ]

INSTALLED_APPS = [
    "jazzmin",
    "modeltranslation",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
    "django_ckeditor_5",
    "hotel.apps.HotelConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.i18n",
                "hotel.context_processors.site_settings",
                "hotel.context_processors.active_promotion",
                "hotel.context_processors.policy_pages",
                "hotel.context_processors.seo",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('POSTGRES_DB', 'stoma'),
        'USER': os.environ.get('POSTGRES_USER', ''),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD', ''),
        'HOST': os.environ.get('POSTGRES_HOST', 'localhost'),
        'PORT': os.environ.get('POSTGRES_PORT', 5432),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "uz"
TIME_ZONE = "Asia/Tashkent"
USE_I18N = True
USE_L10N = True
USE_TZ = True

LANGUAGES = [
    ("uz", _("Uzbek")),
    ("ru", _("Russian")),
    ("en", _("English")),
]

LOCALE_PATHS = [BASE_DIR / "locale"]

MODELTRANSLATION_LANGUAGES = ("uz", "ru", "en")
MODELTRANSLATION_DEFAULT_LANGUAGE = "uz"

LANGUAGE_COOKIE_NAME = "django_language"
LANGUAGE_COOKIE_AGE = 60 * 60 * 24 * 365

STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Uploads: allow larger phone photos; they are compressed on save
DATA_UPLOAD_MAX_MEMORY_SIZE = 25 * 1024 * 1024
FILE_UPLOAD_MAX_MEMORY_SIZE = 25 * 1024 * 1024

CKEDITOR_5_CONFIGS = {
    "default": {
        "toolbar": [
            "heading", "|", "bold", "italic", "link",
            "bulletedList", "numberedList", "blockQuote",
        ],
    }
}

JAZZMIN_SETTINGS = {
    "site_title": "Aida Hotel",
    "site_header": "Aida Hotel",
    "site_brand": "Aida Hotel",
    "site_logo": "images/brand/aida-mark.png",
    "login_logo": "images/brand/aida-logo-header.png",
    "site_logo_classes": "img-circle",
    "site_icon": "images/brand/favicon-32.png",
    "welcome_sign": _("Aida Hotel — Bukhara CMS"),
    "copyright": "Aida Hotel Bukhara",
    "search_model": ["hotel.Booking", "hotel.ContactMessage", "hotel.Room"],
    "user_avatar": None,
    "topmenu_links": [
        {"name": _("Website"), "url": "/", "new_window": True},
        {"name": _("Bookings"), "url": "admin:hotel_booking_changelist"},
        {"name": _("Messages"), "url": "admin:hotel_contactmessage_changelist"},
        {"name": _("Settings"), "model": "hotel.SiteSettings"},
    ],
    "show_sidebar": True,
    "navigation_expanded": True,
    "hide_apps": [],
    "hide_models": [],
    "order_with_respect_to": [
        "hotel",
        "hotel.Booking",
        "hotel.ContactMessage",
        "hotel.RoomType",
        "hotel.Room",
        "hotel.SiteSettings",
        "hotel.HeroSlide",
        "hotel.AboutSection",
        "hotel.GalleryImage",
        "hotel.Amenity",
        "hotel.Testimonial",
        "hotel.FAQ",
        "hotel.Promotion",
        "hotel.StatHighlight",
        "hotel.NearbyPlace",
        "hotel.PolicyPage",
        "auth",
    ],
    "icons": {
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",
        "hotel.Booking": "fas fa-calendar-check",
        "hotel.ContactMessage": "fas fa-envelope-open-text",
        "hotel.RoomType": "fas fa-bed",
        "hotel.Room": "fas fa-door-open",
        "hotel.SiteSettings": "fas fa-cog",
        "hotel.HeroSlide": "fas fa-images",
        "hotel.AboutSection": "fas fa-info-circle",
        "hotel.GalleryImage": "fas fa-camera",
        "hotel.Amenity": "fas fa-concierge-bell",
        "hotel.Testimonial": "fas fa-star",
        "hotel.FAQ": "fas fa-question-circle",
        "hotel.Promotion": "fas fa-tags",
        "hotel.StatHighlight": "fas fa-chart-line",
        "hotel.NearbyPlace": "fas fa-map-marker-alt",
        "hotel.PolicyPage": "fas fa-file-alt",
    },
    "default_icon_parents": "fas fa-folder",
    "default_icon_children": "fas fa-circle",
    "related_modal_active": True,
    "custom_css": "admin/css/aida_admin.css",
    "custom_js": "admin/js/aida_image_compress.js",
    "use_google_fonts_cdn": True,
    "show_ui_builder": False,
    "changeform_format": "horizontal_tabs",
    "changeform_format_overrides": {
        "hotel.sitesettings": "horizontal_tabs",
        "hotel.booking": "horizontal_tabs",
        "hotel.roomtype": "horizontal_tabs",
    },
    "language_chooser": True,
}

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": "navbar-dark",
    "accent": "accent-warning",
    "navbar": "navbar-dark",
    "no_navbar_border": True,
    "navbar_fixed": True,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": True,
    "sidebar": "sidebar-dark-primary",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": True,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": True,
    "theme": "default",
    "dark_mode_theme": None,
    "button_classes": {
        "primary": "btn-warning",
        "secondary": "btn-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success",
    },
    "actions_sticky_top": True,
}

try:
    from .settings_dev import *
except ImportError:
    pass
