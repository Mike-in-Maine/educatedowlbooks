#!/usr/bin/env python3

import time
import requests
import psycopg2
from datetime import datetime

# =========================
# CONFIG
# =========================

DB_CONFIG = {
    "dbname": "eob_catalog",
    "user": "eob_owner",
    "password": "!!!itff2025@@@",
    "host": "localhost",
}

OPENLIB_TIMEOUT = 15
BATCH_SIZE = 50
SLEEP_BETWEEN_BOOKS = 0.7


# =========================
# OPEN LIBRARY FETCH
# =========================

def fetch_openlibrary(isbn13):
    url = "https://openlibrary.org/api/books"
    params = {
        "bibkeys": f"ISBN:{isbn13}",
        "format": "json",
        "jscmd": "data",
    }

    try:
        r = requests.get(url, params=params, timeout=OPENLIB_TIMEOUT)
        r.raise_for_status()

        # OL sometimes returns HTML or empty body
        if not r.text.strip().startswith("{"):
            return None

        raw = r.json().get(f"ISBN:{isbn13}")
        if not raw:
            return None

        # ---- Normalize fields ----

        title = raw.get("title")

        authors = ", ".join(
            a.get("name") for a in raw.get("authors", []) if a.get("name")
        ) or None

        publishers = ", ".join(
            p.get("name") for p in raw.get("publishers", []) if p.get("name")
        ) or None

        publish_date = raw.get("publish_date")
        publish_year = None
        if publish_date:
            digits = "".join(c for c in publish_date if c.isdigit())
            if len(digits) >= 4:
                publish_year = int(digits[:4])

        pages = raw.get("number_of_pages")

        subjects = [
            s.get("name") for s in raw.get("subjects", []) if s.get("name")
        ] or None

        language = None
        if raw.get("languages"):
            language = raw["languages"][0].get("key", "").split("/")[-1]

        description = raw.get("description")
        if isinstance(description, dict):
            description = description.get("value")

        cover_url = None
        if raw.get("cover"):
            cover_url = raw["cover"].get("large") or raw["cover"].get("medium")

        return {
            "isbn13": isbn13,
            "title": title,
            "author": authors,
            "publisher": publishers,
            "publish_year": publish_year,
            "publish_date": publish_date,
            "pages": pages,
            "subjects": subjects,
            "language": language,
            "description": description,
            "cover_url": cover_url,
        }

    except Exception:
        return None


# =========================
# MAIN ENRICHMENT LOOP
# =========================

def main():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    cur.execute("""
        SELECT isbn13
        FROM book_metadata
        WHERE last_enriched IS NULL
        ORDER BY isbn13
        LIMIT %s;

    """, (BATCH_SIZE,))

    rows = cur.fetchall()
    if not rows:
        print("No books to enrich.")
        return

    print(f"Enriching {len(rows)} ISBNs")

    for (isbn13,) in rows:
        print(f"→ {isbn13}")

        data = fetch_openlibrary(isbn13)

        # --------------------------------------------------
        # BAD / EMPTY RESPONSE → MARK ATTEMPTED, SKIP
        # --------------------------------------------------
        if not data:
            cur.execute("""
                UPDATE book_metadata
                SET last_enriched = %(now)s,
                    source = 'openlibrary'
                WHERE isbn13 = %(isbn13)s
            """, {
                "isbn13": isbn13,
                "now": datetime.utcnow()
            })
            conn.commit()
            time.sleep(0.3)
            continue

        # --------------------------------------------------
        # UPSERT CLEAN DATA
        # --------------------------------------------------
        cur.execute("""
            INSERT INTO book_metadata (
                isbn13,
                title,
                author,
                publisher,
                publish_year,
                publish_date,
                pages,
                subjects,
                language,
                description,
                cover_url,
                last_enriched,
                source
            )
            VALUES (
                %(isbn13)s,
                %(title)s,
                %(author)s,
                %(publisher)s,
                %(publish_year)s,
                %(publish_date)s,
                %(pages)s,
                %(subjects)s,
                %(language)s,
                %(description)s,
                %(cover_url)s,
                %(now)s,
                'openlibrary'
            )
            ON CONFLICT (isbn13) DO UPDATE SET
                title = COALESCE(EXCLUDED.title, book_metadata.title),
                author = COALESCE(EXCLUDED.author, book_metadata.author),
                publisher = COALESCE(EXCLUDED.publisher, book_metadata.publisher),
                publish_year = COALESCE(EXCLUDED.publish_year, book_metadata.publish_year),
                publish_date = COALESCE(EXCLUDED.publish_date, book_metadata.publish_date),
                pages = COALESCE(EXCLUDED.pages, book_metadata.pages),
                subjects = COALESCE(EXCLUDED.subjects, book_metadata.subjects),
                language = COALESCE(EXCLUDED.language, book_metadata.language),
                description = COALESCE(EXCLUDED.description, book_metadata.description),
                cover_url = COALESCE(EXCLUDED.cover_url, book_metadata.cover_url),
                last_enriched = EXCLUDED.last_enriched,
                source = 'openlibrary'
        """, {
            **data,
            "now": datetime.utcnow()
        })

        conn.commit()
        time.sleep(SLEEP_BETWEEN_BOOKS)

    cur.close()
    conn.close()


if __name__ == "__main__":
    main()

