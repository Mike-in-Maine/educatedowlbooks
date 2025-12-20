from django.shortcuts import render
from catalog.models import Book

def home(request):
    books = Book.objects.exclude(cover_image="")[:12]  # first 12 with covers
    return render(request, "main/home.html", {"books": books}) 

