from django.urls import path
from .views import public_listings
from . import views


urlpatterns = [
    path("", public_listings, name="public_listings"),
]
