from modeltranslation.translator import TranslationOptions, register

from .models import (
    AboutSection,
    Amenity,
    FAQ,
    GalleryImage,
    HeroSlide,
    NearbyPlace,
    PolicyPage,
    Promotion,
    RoomType,
    SiteSettings,
    StatHighlight,
    Testimonial,
)


@register(SiteSettings)
class SiteSettingsTranslationOptions(TranslationOptions):
    fields = ("site_name", "tagline", "address", "meta_title", "meta_description")


@register(HeroSlide)
class HeroSlideTranslationOptions(TranslationOptions):
    fields = ("title", "subtitle", "cta_text")


@register(AboutSection)
class AboutSectionTranslationOptions(TranslationOptions):
    fields = ("title", "content")


@register(Amenity)
class AmenityTranslationOptions(TranslationOptions):
    fields = ("name", "description")


@register(GalleryImage)
class GalleryImageTranslationOptions(TranslationOptions):
    fields = ("title", "caption")


@register(Testimonial)
class TestimonialTranslationOptions(TranslationOptions):
    fields = ("content",)


@register(FAQ)
class FAQTranslationOptions(TranslationOptions):
    fields = ("question", "answer")


@register(Promotion)
class PromotionTranslationOptions(TranslationOptions):
    fields = ("title", "description", "discount_label")


@register(StatHighlight)
class StatHighlightTranslationOptions(TranslationOptions):
    fields = ("label",)


@register(NearbyPlace)
class NearbyPlaceTranslationOptions(TranslationOptions):
    fields = ("name", "distance")


@register(PolicyPage)
class PolicyPageTranslationOptions(TranslationOptions):
    fields = ("title", "content")


@register(RoomType)
class RoomTypeTranslationOptions(TranslationOptions):
    fields = ("name", "description")
