from django.urls import path, include
from .views import home

urlpatterns = [
    path("", home, name="home"),
    path("books/", include("listings.urls")),
]
