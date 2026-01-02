from django.shortcuts import render
from catalog.models import Book

def home(request):
    books = (
        Book.objects
        .exclude(cover_image="")
        .exclude(last_enriched__isnull=True)
        .order_by("-last_enriched")[:12]
    )
    return render(request, "main/home.html", {"books": books}) 

