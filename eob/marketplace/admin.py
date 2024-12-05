from django.contrib import admin
from .models import Book, Seller  # For marketplace
from marketplace.models import Book, Seller


admin.site.register(Book)
admin.site.register(Seller)