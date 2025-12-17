from django.db.models import Q
from django.shortcuts import render
from .models import Listing


def public_listings(request):
    query = request.GET.get("q", "")

    listings = Listing.objects.select_related(
        "book", "seller"
    )

    if query:
        listings = listings.filter(
            Q(book__title__icontains=query)
            | Q(book__author__icontains=query)
            | Q(book__isbn10__icontains=query)
            | Q(book__isbn13__icontains=query)
        )

    return render(
        request,
        "listings/public_listings.html",
        {
            "listings": listings,
            "query": query,
        },
    )
