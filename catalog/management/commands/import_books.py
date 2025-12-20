import csv
import time
import requests
from pathlib import Path

from django.core.management.base import BaseCommand
from django.conf import settings
from catalog.models import Book


OPENLIB_URL = "https://openlibrary.org/api/books"
MAX_COVER_BYTES = 5 * 1024 * 1024  # 5 MB


class Command(BaseCommand):
    help = "Import books into catalog from ISBN-10 CSV using Open Library (slow & safe)"

    def add_arguments(self, parser):
        parser.add_argument("csv_file", type=str)
        parser.add_argument("--batch-size", type=int, default=1)
        parser.add_argument("--sleep", type=float, default=1.0)

    def handle(self, *args, **options):
        csv_file = options["csv_file"]
        batch_size = options["batch_size"]
        sleep_time = options["sleep"]

        self.stdout.write(self.style.SUCCESS("Starting Open Library catalog import"))

        with open(csv_file, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            isbns = [
                row["isbn10"].strip()
                for row in reader
                if row.get("isbn10") and row["isbn10"].strip()
            ]

        total = len(isbns)
        self.stdout.write(f"Loaded {total} ISBNs")

        for offset in range(0, total, batch_size):
            batch = isbns[offset : offset + batch_size]
            self.process_batch(batch, offset, total)
            time.sleep(sleep_time)

        self.stdout.write(self.style.SUCCESS("Import finished"))

    def process_batch(self, batch, offset, total):
        existing = set(
            Book.objects.filter(isbn10__in=batch)
            .values_list("isbn10", flat=True)
        )

        to_fetch = [isbn for isbn in batch if isbn not in existing]

        if not to_fetch:
            self.stdout.write(f"[{offset}/{total}] already exists, skipping")
            return

        bibkeys = ",".join(f"ISBN:{isbn}" for isbn in to_fetch)

        try:
            r = requests.get(
                OPENLIB_URL,
                params={
                    "bibkeys": bibkeys,
                    "format": "json",
                    "jscmd": "data",
                },
                timeout=20,
            )
        except requests.RequestException as e:
            self.stderr.write(f"[{offset}/{total}] request failed: {e}")
            return

        if r.status_code != 200:
            self.stderr.write(f"[{offset}/{total}] OpenLibrary error")
            return

        data = r.json()
        created = 0

        for key, info in data.items():
            isbn10 = key.replace("ISBN:", "")

            title = info.get("title", "").strip()
            author = ", ".join(a.get("name", "") for a in info.get("authors", []))
            publisher = info.get("publishers", [{}])[0].get("name", "").strip()

            publication_year = None
            if "publish_date" in info:
                digits = "".join(c for c in info["publish_date"] if c.isdigit())
                if len(digits) >= 4:
                    publication_year = int(digits[:4])

            if not title:
                continue

            book = Book.objects.create(
                isbn10=isbn10,
                title=title,
                author=author,
                publisher=publisher,
                publication_year=publication_year,
            )

            # ---- COVER DOWNLOAD ----
            cover_url = None
            if "cover" in info:
                cover_url = (
                    info["cover"].get("large")
                    or info["cover"].get("medium")
                    or info["cover"].get("small")
                )

            if cover_url:
                self.download_cover(book, cover_url)

            created += 1

        self.stdout.write(
            f"[{offset}/{total}] fetched={len(to_fetch)} created={created}"
        )

    def download_cover(self, book, url):
        try:
            r = requests.get(url, stream=True, timeout=20)
        except requests.RequestException:
            return

        if r.status_code != 200:
            return

        content_length = int(r.headers.get("Content-Length", 0))
        if content_length > MAX_COVER_BYTES:
            return

        subdir = book.isbn10[0]
        cover_dir = Path(settings.MEDIA_ROOT) / "catalog" / "covers" / subdir
        cover_dir.mkdir(parents=True, exist_ok=True)

        cover_path = cover_dir / f"{book.isbn10}.jpg"

        with open(cover_path, "wb") as f:
            for chunk in r.iter_content(8192):
                f.write(chunk)

        # Optional: save path to model if you add ImageField later
        # book.cover_image = f"covers/{subdir}/{book.isbn10}.jpg"
        # book.save(update_fields=["cover_image"])
