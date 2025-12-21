import csv
import time
import requests
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from catalog.models import Book

class Command(BaseCommand):
    help = "Import rich book data (Ratings, Social, Descriptions, ASIN) from Open Library"

    def add_arguments(self, parser):
        parser.add_argument("csv_file", type=str)
        parser.add_argument("--sleep", type=float, default=2.0)

    def handle(self, *args, **options):
        csv_file = options["csv_file"]
        sleep_time = options["sleep"]

        with open(csv_file, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                isbn = row.get("isbn10", "").strip()
                if not isbn or Book.objects.filter(isbn10=isbn).exists():
                    continue

                self.stdout.write(f"Processing ISBN: {isbn}...")
                self.import_rich_book(isbn)
                time.sleep(sleep_time)  # Respectful throttling

    def import_rich_book(self, isbn):
        # 1. Fetch Core Data & ASIN (Books API)
        # jscmd=data gives us publishers, pages, and identifiers
        url = f"https://openlibrary.org/api/books?bibkeys=ISBN:{isbn}&format=json&jscmd=data"
        try:
            data_resp = requests.get(url, timeout=15).json().get(f"ISBN:{isbn}", {})
            if not data_resp:
                self.stderr.write(f"No data found for {isbn}")
                return

            # 2. Fetch Work ID & Social Counts (Search API)
            # The Search API is the best place to get aggregated social stats
            search_url = f"https://openlibrary.org/search.json?q=isbn:{isbn}&fields=key,want_to_read_count,already_read_count,currently_reading_count,ratings_average"
            search_resp = requests.get(search_url, timeout=15).json()
            search_doc = search_resp.get("docs", [{}])[0] if search_resp.get("docs") else {}

            # 3. Fetch Description (Works API)
            description = ""
            work_key = search_doc.get("key") # Format: /works/OL123W
            if work_key:
                work_data = requests.get(f"https://openlibrary.org{work_key}.json", timeout=15).json()
                raw_desc = work_data.get("description", "")
                # Description can be a string or a dict {'value': '...'}
                description = raw_desc.get("value", raw_desc) if isinstance(raw_desc, dict) else raw_desc

            # Extraction
            title = data_resp.get("title", "Unknown")
            author_names = ", ".join([a.get("name") for a in data_resp.get("authors", [])])
            publisher = data_resp.get("publishers", [{}])[0].get("name", "")
            
            pub_year = None
            if "publish_date" in data_resp:
                digits = "".join(c for c in data_resp["publish_date"] if c.isdigit())
                if len(digits) >= 4: pub_year = int(digits[:4])

            # New Rich Fields
            book = Book.objects.create(
                isbn10=isbn,
                title=title,
                author=author_names,
                publisher=publisher,
                publication_year=pub_year,
                description=description,
                language=data_resp.get("languages", [{}])[0].get("name", ""),
                pages=data_resp.get("number_of_pages"),
                amazon_asin=data_resp.get("identifiers", {}).get("amazon", [None])[0],
                rating_avg=search_doc.get("ratings_average", 0.0),
                want_to_read_count=search_doc.get("want_to_read_count", 0),
                currently_reading_count=search_doc.get("currently_reading_count", 0),
                already_read_count=search_doc.get("already_read_count", 0),
                preview_url=data_resp.get("preview_url", ""),
            )

            # 4. Handle Cover
            cover_data = data_resp.get("cover", {})
            cover_url = cover_data.get("large") or cover_data.get("medium")
            if cover_url:
                self.download_cover(book, cover_url)

            self.stdout.write(self.style.SUCCESS(f"Successfully imported {title}"))

        except Exception as e:
            self.stderr.write(f"Failed {isbn}: {str(e)}")

    def download_cover(self, book, url):
        try:
            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                book.cover_image.save(f"{book.isbn10}.jpg", ContentFile(r.content), save=True)
        except:
            pass