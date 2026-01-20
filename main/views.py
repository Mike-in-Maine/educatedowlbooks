from django.shortcuts import render
from catalog.models import Book
from django.db.models import Count

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
def categories(request):

    categories = [
        "Fiction",
        "Literature & Fiction",
        "History",
        "Art & Architecture",
        "Science Fiction & Fantasy",
        "Mystery, Thriller & Suspense",
        "Biography & Memoir",
        "Politics & Social Sciences",
        "Philosophy",
        "Religion & Spirituality",
        "Science & Math",
        "Computers & Technology",
        "Business & Economics",
        "Law",
        "Medicine & Health",
        "Travel",
        "Children’s Books",
        "Teen & Young Adult",
        "Comics & Graphic Novels",
        "Cookbooks, Food & Wine",
        "Self-Help & Psychology",
    ]
    formats = (
        Book.objects
        .exclude(format="")
        .values("format")
        .annotate(count=Count("id"))
        .order_by("format")
    )

    languages = (
        Book.objects
        .exclude(language="")
        .values("language")
        .annotate(count=Count("id"))
        .order_by("language")
    )

    eras = [
        {
            "label": "Classics (Before 1970)",
            "query": "classics",
            "count": Book.objects.filter(publication_year__lte=1970).count(),
        },
        {
            "label": "Modern (1970–2000)",
            "query": "modern",
            "count": Book.objects.filter(
                publication_year__gt=1970,
                publication_year__lte=2000,
            ).count(),
        },
        {
            "label": "Contemporary (2000+)",
            "query": "contemporary",
            "count": Book.objects.filter(publication_year__gt=2000).count(),
        },
    ]

    reader_favorites = [
        {
            "label": "Highly Rated (4.0+)",
            "query": "highly-rated",
            "count": Book.objects.filter(rating_avg__gte=4.0).count(),
        },
        {
            "label": "Most Wanted",
            "query": "most-wanted",
            "count": Book.objects.filter(want_to_read_count__gte=100).count(),
        },
    ]

    return render(
        request,
        "main/categories.html",
        {
            "categories": categories,
            "formats": formats,
            "languages": languages,
            "eras": eras,
            "reader_favorites": reader_favorites,
        },
    )
def help_page(request):
    return render(request, "main/help.html")