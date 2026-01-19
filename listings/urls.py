from django.urls import path
from .views import public_listings, upload_inventory
from . import views


urlpatterns = [
    path("", public_listings, name="public_listings"),
    path("sell/upload/", upload_inventory, name="upload_inventory"),
]
