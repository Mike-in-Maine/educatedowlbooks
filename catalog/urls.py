# catalog/urls.py
from django.urls import path
from .views import book_detail

urlpatterns = [
    path("<str:isbn10>/", book_detail, name="book_detail"),
]