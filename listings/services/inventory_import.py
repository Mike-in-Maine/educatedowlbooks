import csv
from io import TextIOWrapper
from decimal import Decimal

from catalog.models import Book
from listings.models import Listing


# ============================================================
# NORMALIZATION HELPERS
# ============================================================

def normalize_condition(value):
    if not value:
        return "good"

    value = value.lower().strip()
    mapping = {
        "new": "new",
        "like new": "like_new",
        "very good": "very_good",
        "good": "good",
        "acceptable": "acceptable",
    }
    return mapping.get(value, "good")


def normalize_format(value):
    if not value:
        return ""

    value = value.lower().strip()
    mapping = {
        "paperback": "paperback",
        "hardcover": "hardcover",
        "mass market": "mass_market",
        "mass market paperback": "mass_market",
    }
    return mapping.get(value, "")


# ============================================================
# BOOK MATCHING (NO SIDE EFFECTS)
# ============================================================

def match_book_from_row(row):
    isbn10 = (row.get("isbn10") or "").strip()
    isbn13 = (row.get("isbn13") or "").strip()

    if isbn10:
        book = Book.objects.filter(isbn10=isbn10).first()
        if book:
            return book

    if isbn13:
        book = Book.objects.filter(isbn13=isbn13).first()
        if book:
            return book

    return None


# ============================================================
# PHASE 1 — ANALYZE CSV (PREVIEW ONLY, SESSION SAFE)
# ============================================================

def analyze_inventory_csv(file, seller):
    """
    Reads CSV and prepares a preview.
    NO database writes.
    NO model instances stored in session.
    """

    wrapper = TextIOWrapper(file, encoding="utf-8")
    reader = csv.DictReader(wrapper)

    headers = reader.fieldnames or []

    preview_rows = []
    matched_books = 0
    missing_books = 0

    for idx, row in enumerate(reader, start=1):
        if idx > 10:  # preview first 10 rows only
            break

        book = match_book_from_row(row)

        if book:
            matched_books += 1
        else:
            missing_books += 1

        preview_rows.append({
            "row": idx,
            "raw": row,  # raw CSV row (dict of strings)
            "book_id": book.id if book else None,
            "book_title": book.title if book else None,
            "book_author": book.author if book else None,
            "isbn10": row.get("isbn10", ""),
            "isbn13": row.get("isbn13", ""),
        })

    return {
        "headers": headers,
        "rows": preview_rows,
        "summary": {
            "sample_size": len(preview_rows),
            "matched_books": matched_books,
            "missing_books": missing_books,
        },
    }


# ============================================================
# PHASE 2 — IMPORT INVENTORY (DB WRITES)
# ============================================================

def import_inventory_csv(preview, seller):
    """
    Creates listings from a confirmed preview.
    """

    results = {
        "created": [],
        "errors": [],
    }

    for item in preview["rows"]:
        row = item["raw"]
        book_id = item.get("book_id")

        book = None
        if book_id:
            book = Book.objects.filter(id=book_id).first()

        if not book:
            results["errors"].append({
                "row": item["row"],
                "error": "Book not found",
                "data": row,
            })
            continue

        try:
            listing = Listing.objects.create(
                seller=seller,
                book=book,
                seller_sku=(row.get("seller_sku") or "").strip(),
                price=Decimal(row.get("price")),
                condition=normalize_condition(row.get("condition")),
                format=normalize_format(row.get("format")),
                quantity=int(row.get("quantity", 1)),
                status="draft",
                created_from="csv",
            )

            results["created"].append(listing)

        except Exception as e:
            results["errors"].append({
                "row": item["row"],
                "error": str(e),
                "data": row,
            })

    return results
