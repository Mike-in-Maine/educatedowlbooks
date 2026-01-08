from django.urls import path, include
from .views import home, categories

urlpatterns = [
    path("", home, name="home"),
    path("categories/", categories, name="categories"),
]
