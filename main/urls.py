from django.urls import path, include
from .views import home, categories, help_page

urlpatterns = [
    path("", home, name="home"),
    path("categories/", categories, name="categories"),
    path("help/", help_page, name="help"),
]
