import os
from django.db import models

def get_catalog_upload_path(instance, filename):
    """
    Generates a partitioned path for book covers.
    Example: ISBN 0123456789 -> catalog/covers/0/1/2/0123456789.jpg
    """
    isbn = instance.isbn10 or instance.isbn13 or "unknown"
    return os.path.join('catalog', 'covers', *isbn[:3], filename)

class Book(models.Model):
    # Identifiers
    isbn10 = models.CharField(
        max_length=10, unique=True, null=True, blank=True, db_index=True,
        help_text="Primary identifier when available",
    )
    isbn13 = models.CharField(
        max_length=13, unique=True, null=True, blank=True, db_index=True,
    )
    amazon_asin = models.CharField(
        max_length=20, blank=True, null=True, help_text="Amazon Standard Identification Number"
    )

    # Core Metadata
    title = models.CharField(max_length=512)
    author = models.CharField(max_length=512, blank=True)
    publisher = models.CharField(max_length=255, blank=True)
    publication_year = models.PositiveSmallIntegerField(null=True, blank=True)
    
    # Rich Content
    description = models.TextField(blank=True, null=True)
    language = models.CharField(max_length=32, blank=True)
    pages = models.PositiveIntegerField(null=True, blank=True)
    format = models.CharField(
        max_length=64, blank=True, help_text="Hardcover, Paperback, etc.",
    )

    # Social & Stats
    rating_avg = models.FloatField(default=2.0)
    want_to_read_count = models.IntegerField(default=0)
    currently_reading_count = models.IntegerField(default=0)
    already_read_count = models.IntegerField(default=0)
    preview_url = models.URLField(blank=True, null=True)

    # Media
    cover_image = models.ImageField(
        upload_to=get_catalog_upload_path,
        blank=True, null=True,
        help_text="Cover image of the book",
    )
    cover_openlibrary_id = models.CharField(max_length=32, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["title"]
        indexes = [
            models.Index(fields=["title"]),
            models.Index(fields=["author"]),
        ]

    def __str__(self):
        return f"{self.title} ({self.author})" if self.author else self.title