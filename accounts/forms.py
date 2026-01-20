from django import forms
from .models import Seller

class SellerOnboardingForm(forms.ModelForm):
    class Meta:
        model = Seller
        fields = ["display_name", "country"]
        widgets = {
            "display_name": forms.TextInput(attrs={
                "placeholder": "Your bookstore name"
            }),
            "country": forms.TextInput(attrs={
                "placeholder": "US, IT, UK, etc."
            }),
        }
