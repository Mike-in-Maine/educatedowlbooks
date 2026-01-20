from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views


urlpatterns = [
    path("secure-admin-9xQp/", admin.site.urls),
    path("", include("main.urls")),
    path("books/", include("listings.urls")),
    path("catalog/", include("catalog.urls")),

    # AUTH (use accounts template)
    path("login/", auth_views.LoginView.as_view(template_name="accounts/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(template_name="accounts/logout.html"), name="logout"),

    # SELLER ONBOARDING URLS
    path("accounts/", include("accounts.urls")),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )