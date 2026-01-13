import requests
import time
import json

# =========================
# CONFIG
# =========================

ISBN_LIST = [
    "0068596022",
    "1335009833",
    "0060950196",
    "0385494122",
    "0050014234",
    "0736908552",
]

LOC_BASE = "https://www.loc.gov/books/"
OL_SEARCH = "https://openlibrary.org/search.json"

HEADERS = {
    "User-Agent": "EducatedOwlBooks/0.1 (testing LoC integration)"
}

# =========================
# UTILITIES
# =========================

def isbn10_to_isbn13(isbn10: str) -> str:
    """
    Convert ISBN-10 to ISBN-13.
    """
    core = "978" + isbn10[:-1]
    total = 0
    for i, ch in enumerate(core):
        total += int(ch) * (1 if i % 2 == 0 else 3)
    check = (10 - (total % 10)) % 10
    return core + str(check)


def fetch_loc_by_isbn(isbn13: str):
    """
    Query Library of Congress by ISBN-13.
    """
    params = {
        "fo": "json",
        "q": f"isbn:{isbn13}",
    }
    r = requests.get(LOC_BASE, params=params, headers=HEADERS, timeout=15)
    r.raise_for_status()
    data = r.json()
    results = data.get("results", [])
    return results[0] if results else None


def fetch_ol_title_author(isbn: str):
    """
    Resolve ISBN → title + author via Open Library.
    """
    params = {
        "q": f"isbn:{isbn}",
        "fields": "title,author_name",
        "limit": 1,
    }
    r = requests.get(OL_SEARCH, params=params, timeout=15)
    r.raise_for_status()
    docs = r.json().get("docs", [])
    if not docs:
        return None

    doc = docs[0]
    title = doc.get("title")
    author = doc.get("author_name", [None])[0]

    if title and author:
        return title, author

    return None


def fetch_loc_by_title_author(title: str, author: str):
    """
    Fallback LoC search using bibliographic query.
    """
    query = f"{title} {author}"
    params = {
        "fo": "json",
        "q": query,
    }
    r = requests.get(LOC_BASE, params=params, headers=HEADERS, timeout=15)
    r.raise_for_status()
    data = r.json()
    results = data.get("results", [])
    return results[0] if results else None


def summarize_loc_record(rec: dict):
    """
    Extract all useful bibliographic fields from a LoC record.
    """
    return {
        "title": rec.get("title"),
        "contributors": rec.get("contributor"),
        "edition": rec.get("edition"),
        "publisher": rec.get("publisher"),
        "place": rec.get("place"),
        "publication_date": rec.get("date"),
        "language": rec.get("language"),
        "physical_description": rec.get("physical_description"),
        "subjects": rec.get("subject"),
        "lcc": rec.get("lcc"),
        "dewey": rec.get("dewey"),
        "identifiers": rec.get("identifier"),
        "lccn": rec.get("lccn"),
        "notes": rec.get("note"),
    }

# =========================
# MAIN
# =========================

def main():
    for isbn10 in ISBN_LIST:
        print("=" * 90)
        print(f"ISBN-10: {isbn10}")

        isbn13 = isbn10_to_isbn13(isbn10)
        print(f"ISBN-13: {isbn13}")

        # ---- 1. Try LoC by ISBN-13 ----
        try:
            loc_rec = fetch_loc_by_isbn(isbn13)
        except Exception as e:
            print(f"ERROR querying LoC by ISBN: {e}")
            continue

        if loc_rec:
            print("✅ LoC hit via ISBN-13\n")
            print(json.dumps(summarize_loc_record(loc_rec), indent=2, ensure_ascii=False))
            time.sleep(1)
            continue

        print("⚠️ No LoC record via ISBN — trying Open Library fallback")

        # ---- 2. Resolve via Open Library ----
        try:
            resolved = fetch_ol_title_author(isbn10)
        except Exception as e:
            print(f"ERROR querying Open Library: {e}")
            continue

        if not resolved:
            print("❌ Open Library could not resolve title/author")
            continue

        title, author = resolved
        print(f"Resolved via OL → Title: {title} | Author: {author}")

        # ---- 3. Try LoC via title+author ----
        try:
            loc_rec = fetch_loc_by_title_author(title, author)
        except Exception as e:
            print(f"ERROR querying LoC by title/author: {e}")
            continue

        if loc_rec:
            print("✅ LoC hit via title/author\n")
            print(json.dumps(summarize_loc_record(loc_rec), indent=2, ensure_ascii=False))
        else:
            print("❌ No LoC record found after all fallbacks")

        time.sleep(1)


if __name__ == "__main__":
    main()
