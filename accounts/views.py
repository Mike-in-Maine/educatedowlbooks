from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import SellerOnboardingForm

@login_required
def seller_onboarding(request):
    if hasattr(request.user, "seller_profile"):
        return redirect("seller_listings")

    if request.method == "POST":
        form = SellerOnboardingForm(request.POST)
        if form.is_valid():
            seller = form.save(commit=False)
            seller.user = request.user
            seller.save()
            return redirect("seller_listings")
    else:
        form = SellerOnboardingForm()

    return render(request, "accounts/seller_onboarding.html", {
        "form": form
    })
