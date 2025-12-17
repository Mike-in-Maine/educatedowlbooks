from django.urls import path
from .views import public_listings

urlpatterns = [
    path("", public_listings, name="public_listings"),
]
