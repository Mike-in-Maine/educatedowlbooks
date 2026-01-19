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

    FORMAT_CHOICES = [
        ("paperback", "Paperback"),
        ("hardcover", "Hardcover"),
        ("mass_market", "Mass Market Paperback"),
    ]

    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("active", "Active"),
        ("sold", "Sold"),
        ("archived", "Archived"),
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

    seller_sku = models.CharField(
        max_length=100,
        blank=True,
        help_text="Seller’s internal reference / SKU",
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    format = models.CharField(
        max_length=32,
        choices=FORMAT_CHOICES,
        blank=True,
    )

    condition = models.CharField(
        max_length=20,
        choices=CONDITION_CHOICES,
    )

    quantity = models.PositiveIntegerField(default=1)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="draft",
        db_index=True,
    )

    created_from = models.CharField(
        max_length=50,
        blank=True,
        help_text="csv, manual, api, etc.",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["price"]
        indexes = [
            models.Index(fields=["price"]),
            models.Index(fields=["condition"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"{self.book.title} — {self.seller.display_name}"
