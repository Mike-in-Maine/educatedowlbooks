from django.contrib import admin
from .models import Listing


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = (
        "book",
        "seller",
        "price",
        "condition",
        "quantity",
    )
    list_filter = ("condition", "seller")
    search_fields = ("book__title", "book__author", "seller__display_name")
