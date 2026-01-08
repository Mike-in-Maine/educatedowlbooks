# catalog/views.py
from django.shortcuts import get_object_or_404, render
from django.db.models import Q
from .models import Book

def book_detail(request, identifier):
    book = get_object_or_404(
        Book,
        Q(isbn10=identifier) | Q(isbn13=identifier)
    )

    listings_qs = (
        book.listings
        .select_related("seller")
        .filter(quantity__gt=0)
        .order_by("price")
    )

    primary_listing = listings_qs.first()
    other_listings = listings_qs[1:]

    return render(
        request,
        "book_detail.html",
        {
            "book": book,
            "primary_listing": primary_listing,
            "other_listings": other_listings,
        }
    )
