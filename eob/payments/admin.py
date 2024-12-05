from django.contrib import admin
from .models import Book, Seller  # For marketplace

admin.site.register(Book)
admin.site.register(Seller)