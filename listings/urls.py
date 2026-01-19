from django.urls import path
from .views import *
from . import views


urlpatterns = [
    # Public buyer view
    path("", public_listings, name="public_listings"),

    # Seller inventory upload flow
    path("upload/", upload_inventory, name="upload_inventory"),
    path("upload/confirm/", confirm_inventory, name="confirm_inventory"),

    # Seller listings dashboard
    path("my-listings/", seller_listings, name="seller_listings"),
    path("my-listings/publish/<int:listing_id>/",publish_listing,name="publish_listing",),
]
