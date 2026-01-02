# catalog/views.py
from django.shortcuts import get_object_or_404, render
from .models import Book

def book_detail(request, isbn13):
    book = get_object_or_404(Book, isbn13=isbn13)
    listings = book.listings.select_related("seller").order_by("price")
    return render(
        request,
        "book_detail.html",
        {
            "book": book,
            "listings": listings,
        }
    )
