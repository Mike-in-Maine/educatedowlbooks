from functools import wraps
from django.shortcuts import redirect

def seller_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("login")

        if not hasattr(request.user, "seller_profile"):
            return redirect("seller_onboarding")

        return view_func(request, *args, **kwargs)

    return wrapper
