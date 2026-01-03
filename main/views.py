from django.shortcuts import render
from catalog.models import Book
from django.db.models import Q

def home(request):
    recently_enriched = (
        Book.objects
        .filter(last_enriched__isnull=False)
        .exclude(cover_image="")
        .order_by("-last_enriched")[:10]
    )

    highly_rated = (
        Book.objects
        .filter(rating_avg__gte=4.0)
        .exclude(cover_image="")
        .order_by("-rating_avg")[:10]
    )

    classics = (
        Book.objects
        .filter(publication_year__lte=1970)
        .exclude(cover_image="")
        .order_by("publication_year")[:15]
    )

    return render(
        request,
        "main/home.html",
        {
            "recently_enriched": recently_enriched,
            "highly_rated": highly_rated,
            "classics": classics,
        }
    )
