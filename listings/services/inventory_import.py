import csv
from decimal import Decimal
from catalog.models import Book
from listings.models import Listing


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


def match_book(row):
    isbn10 = row.get("isbn10", "").strip()
    isbn13 = row.get("isbn13", "").strip()

    if isbn10:
        book = Book.objects.filter(isbn10=isbn10).first()
        if book:
            return book

    if isbn13:
        book = Book.objects.filter(isbn13=isbn13).first()
        if book:
            return book

    return None



def import_inventory_csv(file, seller):
    decoded = file.read().decode("utf-8").splitlines()
    reader = csv.DictReader(decoded)

    results = {
        "created": [],
        "errors": [],
    }

    for idx, row in enumerate(reader, start=1):
        book = match_book(row)
        if not book:
            results["errors"].append(
                {"row": idx, "error": "Book not found", "data": row}
            )
            continue

        try:
            listing = Listing.objects.create(
                seller=seller,
                book=book,
                seller_sku=row.get("seller_sku", "").strip(),
                price=Decimal(row["price"]),
                condition=normalize_condition(row.get("condition")),
                format=normalize_format(row.get("format")),
                quantity=int(row.get("quantity", 1)),
                status="draft",
                created_from="csv",
            )
            results["created"].append(listing)

        except Exception as e:
            results["errors"].append(
                {"row": idx, "error": str(e), "data": row}
            )
    print(reader.fieldnames)

    return results
