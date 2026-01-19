from django.db.models import Q
from .models import Listing
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from accounts.models import Seller
from .services.inventory_import import import_inventory_csv


def public_listings(request):
    query = request.GET.get("q", "")
    format_filter = request.GET.get("format")
    language_filter = request.GET.get("language")
    era = request.GET.get("era")
    special = request.GET.get("special")

    listings = Listing.objects.select_related("book", "seller")

    if query:
        listings = listings.filter(
            Q(book__title__icontains=query)
            | Q(book__author__icontains=query)
            | Q(book__isbn10__icontains=query)
            | Q(book__isbn13__icontains=query)
        )

    if format_filter:
        listings = listings.filter(book__format=format_filter)

    if language_filter:
        listings = listings.filter(book__language=language_filter)

    if era == "classics":
        listings = listings.filter(book__publication_year__lte=1970)
    elif era == "modern":
        listings = listings.filter(
            book__publication_year__gt=1970,
            book__publication_year__lte=2000,
        )
    elif era == "contemporary":
        listings = listings.filter(book__publication_year__gt=2000)

    if special == "highly-rated":
        listings = listings.filter(book__rating_avg__gte=4.0)
    elif special == "most-wanted":
        listings = listings.filter(book__want_to_read_count__gte=100)

    return render(
        request,
        "listings/public_listings.html",
        {
            "listings": listings,
            "query": query,
        },
    )
@login_required
def upload_inventory(request):
    seller = getattr(request.user, "seller_profile", None)
    if not seller:
        return render(request, "listings/not_a_seller.html")

    context = {}

    if request.method == "POST" and request.FILES.get("file"):
        results = import_inventory_csv(
            request.FILES["file"],
            seller,
        )
        context["results"] = results

    return render(request, "listings/upload_inventory.html", context)