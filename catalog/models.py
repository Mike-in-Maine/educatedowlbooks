import os
from django.db import models

def get_catalog_upload_path(instance, filename):
    """
    Generates a partitioned path for book covers.
    Example: ISBN 0123456789 -> catalog/covers/0/1/2/0123456789.jpg
    """
    # Prefer isbn10, fallback to isbn13, use 'unknown' if neither exists
    isbn = instance.isbn10 or instance.isbn13 or "unknown"
    
    # Take the first 3 characters to create a 3-level deep directory structure
    # This safely handles 100k+ files by spreading them across 1000 potential folders
    chars = [char for char in isbn[:3]]
    
    # Returns 'catalog/covers/0/1/2/filename.jpg'
    return os.path.join('catalog', 'covers', *chars, filename)

class Book(models.Model):
    isbn10 = models.CharField(
        max_length=10,
        unique=True,
        null=True,
        blank=True,
        db_index=True,
        help_text="Primary identifier when available",
    )
    isbn13 = models.CharField(
        max_length=13,
        unique=True,
        null=True,
        blank=True,
        db_index=True,
    )

    title = models.CharField(max_length=512)
    author = models.CharField(max_length=512, blank=True)
    publisher = models.CharField(max_length=255, blank=True)
    publication_year = models.PositiveSmallIntegerField(null=True, blank=True)

    language = models.CharField(max_length=32, blank=True)
    format = models.CharField(
        max_length=64,
        blank=True,
        help_text="Hardcover, Paperback, etc.",
    )

    # Use the function defined above for upload_to
    cover_image = models.ImageField(
        upload_to=get_catalog_upload_path,
        blank=True,
        null=True,
        help_text="Cover image of the book",
    )

    cover_openlibrary_id = models.CharField(
        max_length=32,
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["title"]
        indexes = [
            models.Index(fields=["title"]),
            models.Index(fields=["author"]),
        ]

    def __str__(self):
        return f"{self.title} ({self.author})" if self.author else self.title