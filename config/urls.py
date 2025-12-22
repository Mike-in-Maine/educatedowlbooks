from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("secure-admin-9xQp/", admin.site.urls),
    path("", include("main.urls")),
    path("books/", include("listings.urls")),
    path("catalog/", include("catalog.urls")),

]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )