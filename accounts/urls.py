from django.urls import path
from .views import seller_onboarding

urlpatterns = [
    path("onboarding/", seller_onboarding, name="seller_onboarding"),
]
