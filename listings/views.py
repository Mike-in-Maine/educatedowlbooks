from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from .models import Listing
from accounts.models import Seller

from .services.inventory_import import (analyze_inventory_csv,import_inventory_csv)


# ============================================================
# PUBLIC LISTINGS (BUYER VIEW)
# ============================================================

def public_listings(request):
    query = request.GET.get("q", "")
    format_filter = request.GET.get("format")
    language_filter = request.GET.get("language")
    era = request.GET.get("era")
    special = request.GET.get("special")

    listings = (
        Listing.objects
        .select_related("book", "seller")
        .filter(status="active", quantity__gt=0)
    )

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


# ============================================================
# SELLER: UPLOAD INVENTORY (PREVIEW ONLY)
# ============================================================

@login_required
def upload_inventory(request):
    seller = getattr(request.user, "seller_profile", None)
    if not seller:
        return render(request, "listings/not_a_seller.html")

    context = {}

    if request.method == "POST" and request.FILES.get("file"):
        preview = analyze_inventory_csv(
            request.FILES["file"],
            seller,
        )

        # Store preview in session (JSON-safe)
        request.session["inventory_preview"] = preview

        context["preview"] = preview
        context["awaiting_confirmation"] = True

    return render(
        request,
        "listings/upload_inventory.html",
        context,
    )


# ============================================================
# SELLER: CONFIRM & IMPORT INVENTORY (DB WRITES)
# ============================================================

@login_required
def confirm_inventory(request):
    seller = getattr(request.user, "seller_profile", None)
    if not seller:
        return redirect("upload_inventory")

    preview = request.session.get("inventory_preview")
    if not preview:
        return redirect("upload_inventory")

    if request.method == "POST":
        results = import_inventory_csv(
            preview,
            seller,
        )

        # Clean up session
        try:
            del request.session["inventory_preview"]
        except KeyError:
            pass

        return render(
            request,
            "listings/import_results.html",
            {
                "results": results,
            },
        )

    return redirect("upload_inventory")


# ============================================================
# SELLER: MY LISTINGS (DRAFT + ACTIVE)
# ============================================================

@login_required
def seller_listings(request):
    seller = getattr(request.user, "seller_profile", None)
    if not seller:
        return render(request, "listings/not_a_seller.html")

    listings = (
        Listing.objects
        .select_related("book")
        .filter(seller=seller)
        .order_by("status", "-created_at")
    )

    return render(
        request,
        "listings/seller_listings.html",
        {
            "listings": listings,
        },
    )


# ============================================================
# SELLER: PUBLISH A DRAFT LISTING
# ============================================================

@login_required
def publish_listing(request, listing_id):
    seller = getattr(request.user, "seller_profile", None)
    if not seller:
        return redirect("seller_listings")

    listing = get_object_or_404(
        Listing,
        id=listing_id,
        seller=seller,
        status="draft",
    )

    listing.status = "active"
    listing.save(update_fields=["status"])

    return redirect("seller_listings")
