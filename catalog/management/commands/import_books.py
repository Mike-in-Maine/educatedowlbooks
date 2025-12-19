import csv
import time
import requests

from django.core.management.base import BaseCommand
from catalog.models import Book

OPENLIB_URL = "https://openlibrary.org/api/books"


class Command(BaseCommand):
    help = "Import books into catalog from ISBN-10 CSV using Open Library (slow & safe)"

    def add_arguments(self, parser):
        parser.add_argument(
            "csv_file",
            type=str,
            help="CSV file containing an 'isbn10' column",
        )
        parser.add_argument(
            "--batch-size",
            type=int,
            default=1,
            help="ISBNs per request (default: 1)",
        )
        parser.add_argument(
            "--sleep",
            type=float,
            default=1.0,
            help="Seconds to sleep between requests",
        )

    def handle(self, *args, **options):
        csv_file = options["csv_file"]
        batch_size = options["batch_size"]
        sleep_time = options["sleep"]

        self.stdout.write(self.style.SUCCESS("Starting Open Library catalog import"))

        # Load ISBNs from CSV
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
            response = requests.get(
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

        if response.status_code != 200:
            self.stderr.write(
                f"[{offset}/{total}] OpenLibrary error {response.status_code}"
            )
            return

        data = response.json()
        created = 0

        for key, info in data.items():
            isbn10 = key.replace("ISBN:", "")

            title = info.get("title", "").strip()
            author = ", ".join(
                a.get("name", "") for a in info.get("authors", [])
            )
            publisher = (
                info.get("publishers", [{}])[0].get("name", "").strip()
            )

            publication_year = None
            if "publish_date" in info:
                digits = "".join(c for c in info["publish_date"] if c.isdigit())
                if len(digits) >= 4:
                    publication_year = int(digits[:4])

            if not title:
                continue

            Book.objects.create(
                isbn10=isbn10,
                title=title,
                author=author,
                publisher=publisher,
                publication_year=publication_year,
            )
            created += 1

        self.stdout.write(
            f"[{offset}/{total}] fetched={len(to_fetch)} created={created}"
        )
