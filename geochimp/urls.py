from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("", include("photo_tagger.urls")),
    path("docusign/", include("docusign.urls")),
    path("map/", include("map.urls")),
    path("admin/", admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += [
        path("__reload__/", include("django_browser_reload.urls")),
    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
