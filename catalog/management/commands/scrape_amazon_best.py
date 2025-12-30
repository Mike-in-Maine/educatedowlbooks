import csv
import random
import re
import time
import os
from dataclasses import dataclass
from typing import List, Dict

from bs4 import BeautifulSoup
from curl_cffi import requests


# =========================
# CONFIG
# =========================

SUBCATEGORIES = [
    "https://www.amazon.com/Best-Sellers-Books-Romance/zgbs/books/23",

]

MAX_ITEMS_PER_PAGE = 30

# Amazon needs BIG delays
AMAZON_SLEEP_MIN = 300     # 5 minutes
AMAZON_SLEEP_MAX = 900     # 15 minutes

OPENLIB_SLEEP_MIN = 1
OPENLIB_SLEEP_MAX = 3

OUTPUT_FILE = "amazon_seed_books.csv"


# =========================
# REGEX / STRUCTURES
# =========================

ASIN_RE = re.compile(r"/dp/([A-Z0-9]{10})")


@dataclass
class AmazonItem:
    rank: int
    asin: str
    title: str
    author: str
    url: str


# =========================
# UTILITIES
# =========================

def sleep_range(a, b, label=""):
    t = random.uniform(a, b)
    print(f"Sleeping {t:.1f}s {label}")
    time.sleep(t)


def amazon_session():
    s = requests.Session(impersonate="chrome120")
    s.headers.update({
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Upgrade-Insecure-Requests": "1",
        "Referer": "https://www.amazon.com/",
        "DNT": "1",
    })
    return s


def ensure_csv_header(path: str, fieldnames: List[str]):
    if not os.path.exists(path):
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()


def append_rows(path: str, rows: List[Dict]):
    if not rows:
        return
    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writerows(rows)


# =========================
# AMAZON
# =========================

def fetch_html(session, url):
    r = session.get(url, timeout=20)
    html = r.text or ""

    if r.status_code in (429, 503):
        raise RuntimeError("Amazon rate-limited")
    if "captcha" in html.lower():
        raise RuntimeError("Amazon CAPTCHA detected")

    return html


def parse_items(html: str) -> List[AmazonItem]:
    soup = BeautifulSoup(html, "lxml")
    items = []

    blocks = soup.select("div.zg-grid-general-faceout")
    for i, block in enumerate(blocks, start=1):
        link = block.find("a", href=re.compile(r"/dp/"))
        if not link:
            continue

        href = link.get("href", "")
        m = ASIN_RE.search(href)
        if not m:
            continue

        asin = m.group(1)
        url = "https://www.amazon.com" + href.split("?")[0]

        title = ""
        img = block.find("img")
        if img and img.get("alt"):
            title = img["alt"].strip()

        author = ""
        for s in block.select("a.a-size-small, span.a-size-small"):
            t = s.get_text(strip=True)
            if t and not any(k in t.lower() for k in ["paperback", "hardcover", "kindle"]):
                author = t
                break

        if title and author:
            items.append(AmazonItem(i, asin, title, author, url))

        if len(items) >= MAX_ITEMS_PER_PAGE:
            break

    return items


# =========================
# OPEN LIBRARY (AUTHORITATIVE)
# =========================

def openlibrary_lookup(title, author):
    q = f"{title} {author}".strip()

    r = requests.get(
        "https://openlibrary.org/search.json",
        params={
            "q": q,
            "fields": "key,title,author_name,isbn",
            "limit": 5,
        },
        timeout=15,
    )

    if r.status_code != 200:
        return None

    for d in r.json().get("docs", []):
        isbns = d.get("isbn") or []
        isbn10 = next((x for x in isbns if len(x) == 10), "")
        isbn13 = next((x for x in isbns if len(x) == 13), "")

        if isbn10 or isbn13:
            return {
                "isbn10": isbn10,
                "isbn13": isbn13,
                "ol_key": d.get("key", ""),
            }

    return None


# =========================
# MAIN
# =========================

def main():
    # Pick ONE category per run
    subcat = random.choice(SUBCATEGORIES)
    print(f"Selected subcategory: {subcat}")

    session = amazon_session()

    fieldnames = [
        "rank",
        "amazon_asin",
        "amazon_title",
        "amazon_author",
        "amazon_url",
        "isbn10",
        "isbn13",
        "ol_key",
        "subcategory_url",
    ]

    ensure_csv_header(OUTPUT_FILE, fieldnames)

    try:
        html = fetch_html(session, subcat)
    except RuntimeError as e:
        print(f"Stopping run due to Amazon block: {e}")
        return

    items = parse_items(html)
    print(f"Parsed {len(items)} Amazon items")

    seen = set()
    rows = []

    for it in items:
        sleep_range(OPENLIB_SLEEP_MIN, OPENLIB_SLEEP_MAX, "(Open Library)")

        ol = openlibrary_lookup(it.title, it.author)
        if not ol:
            continue

        dedupe_key = ol.get("isbn10") or ol.get("isbn13") or ol.get("ol_key")
        if dedupe_key in seen:
            continue
        seen.add(dedupe_key)

        rows.append({
            "rank": it.rank,
            "amazon_asin": it.asin,
            "amazon_title": it.title,
            "amazon_author": it.author,
            "amazon_url": it.url,
            "isbn10": ol.get("isbn10", ""),
            "isbn13": ol.get("isbn13", ""),
            "ol_key": ol.get("ol_key", ""),
            "subcategory_url": subcat,
        })

    append_rows(OUTPUT_FILE, rows)
    print(f"Saved {len(rows)} rows")

    print("\nRun complete (single Amazon page).")


if __name__ == "__main__":
    main()
