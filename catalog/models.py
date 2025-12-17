from django.db import models


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

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["title"]
        indexes = [
            models.Index(fields=["title"]),
            models.Index(fields=["author"]),
        ]

    def __str__(self):
        return self.title
