from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path

from hotel.sitemaps import PolicyPageSitemap, RoomTypeSitemap, StaticViewSitemap
from hotel.views import favicon, robots_txt, switch_language

sitemaps = {
    "static": StaticViewSitemap,
    "rooms": RoomTypeSitemap,
    "policies": PolicyPageSitemap,
}

urlpatterns = [
    path("i18n/", include("django.conf.urls.i18n")),
    path("lang/<str:lang_code>/", switch_language, name="switch_language"),
    path("favicon.ico", favicon, name="favicon"),
    path("robots.txt", robots_txt, name="robots_txt"),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="sitemap"),
]

urlpatterns += i18n_patterns(
    path("admin/", admin.site.urls),
    path("", include("hotel.urls")),
    prefix_default_language=False,
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])

handler404 = "hotel.views.page_not_found"
handler500 = "hotel.views.server_error"
