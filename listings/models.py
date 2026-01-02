from django.db import models
from catalog.models import Book
from accounts.models import Seller


class Listing(models.Model):
    CONDITION_CHOICES = [
        ("new", "New"),
        ("like_new", "Like New"),
        ("very_good", "Very Good"),
        ("good", "Good"),
        ("acceptable", "Acceptable"),
    ]

    seller = models.ForeignKey(
        Seller,
        on_delete=models.CASCADE,
        related_name="listings",
    )

    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name="listings",
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    format = models.CharField(
        max_length=32,
        blank=True,
        help_text="Paperback, Hardcover, etc."
    )


    condition = models.CharField(
        max_length=20,
        choices=CONDITION_CHOICES,
    )

    quantity = models.PositiveIntegerField(default=1)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["price"]
        indexes = [
            models.Index(fields=["price"]),
            models.Index(fields=["condition"]),
        ]

    def __str__(self):
        return f"{self.book.title} — {self.seller.display_name}"
