import csv
from django.core.management.base import BaseCommand
from django.utils.dateparse import parse_datetime
from catalog.models import Book


class Command(BaseCommand):
    help = "Import enriched sample books into DEV database"

    def add_arguments(self, parser):
        parser.add_argument("csv_file", type=str)

    def handle(self, *args, **options):
        path = options["csv_file"]

        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            for row in reader:
                Book.objects.update_or_create(
                    isbn13=row["isbn13"],
                    defaults={
                        "title": row["title"],
                        "author": row["author"],
                        "publisher": row["publisher"],
                        "publication_year": row["publication_year"] or None,
                        "description": row["description"],
                        "last_enriched": parse_datetime(row["last_enriched"]),
                    },
                )

        self.stdout.write(self.style.SUCCESS("DEV sample import complete"))
