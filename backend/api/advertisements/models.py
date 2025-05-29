from django.db import models
from uuid import uuid4
from .constants import *
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.conf import settings


class ProductImage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    image = models.ImageField(
        upload_to="product_images/",
        help_text=_("Upload product images (max 5MB, formats: jpeg, png, gif)"),
    )
    product = models.ForeignKey(
        "Product", on_delete=models.CASCADE, related_name="images"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["created_at"]
        verbose_name = _("Product Image")
        verbose_name_plural = _("Product Images")

    def __str__(self):
        return f"Image for {self.product.title}"


class PricingTier(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    product = models.ForeignKey(
        "Product", on_delete=models.CASCADE, related_name="pricing_tiers"
    )
    duration_unit = models.CharField(
        max_length=255,
        choices=DURATION_UNITS,
        help_text=_("Rental duration unit (day/week/month)"),
    )
    base_price = models.PositiveIntegerField(
        help_text=_("Base price for the rental period")
    )
    max_period = models.PositiveIntegerField(
        null=True, blank=True, help_text=_("Maximum rental period (optional)")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["duration_unit", "base_price"]
        unique_together = ["product", "duration_unit"]
        verbose_name = _("Pricing Tier")
        verbose_name_plural = _("Pricing Tiers")
        constraints = [
            models.UniqueConstraint(
                fields=["product", "duration_unit"],
                name="unique_duration_unit_per_product",
            )
        ]

    def __str__(self):
        return f"{self.product.title} - {self.duration_unit}: ({self.base_price}) (max period: {self.max_period})"


class UnavailablePeriod(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    product = models.ForeignKey(
        "Product", on_delete=models.CASCADE, related_name="unavailable_periods"
    )
    single_date = models.DateField(
        null=True, blank=True, help_text=_("Single unavailable date")
    )
    is_range = models.BooleanField(
        default=False, help_text=_("Whether this is a date range")
    )
    range_start = models.DateField(
        null=True, blank=True, help_text=_("Start date of unavailable period")
    )
    range_end = models.DateField(
        null=True, blank=True, help_text=_("End date of unavailable period")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-range_start", "-single_date"]
        verbose_name = _("Unavailable Period")
        verbose_name_plural = _("Unavailable Periods")

    def __str__(self):
        if self.is_range:
            return f"{self.product.title} - Unavailable from {self.range_start} to {self.range_end}"
        return f"{self.product.title} - Unavailable on {self.single_date}"


class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="products")
    title = models.CharField(max_length=255, help_text=_("Product title"))
    category = models.CharField(
        max_length=255,
        choices=CATEGORY_CHOICES,
        help_text=_("Product category"),
    )
    product_type = models.CharField(
        max_length=255,
        choices=PRODUCT_TYPE_CHOICES,
        help_text=_("Product type"),
    )
    description = models.TextField(help_text=_("Product description"))
    location = models.CharField(max_length=255, help_text=_("Product location"))
    security_deposit = models.PositiveIntegerField(
        null=True, blank=True, help_text=_("Security deposit amount (optional)")
    )
    purchase_year = models.DateField(help_text=_("Year of purchase"))
    purchase_price = models.PositiveIntegerField(help_text=_("Original purchase price"))
    ownership_history = models.CharField(
        max_length=255,
        choices=OWNERSHIP_HISTORY_CHOICES,
        help_text=_("Product ownership history"),
    )
    status = models.CharField(
        max_length=255,
        choices=STATUS_CHOICES,
        default="draft",
        help_text=_("Product status"),
    )
    status_message = models.TextField(
        null=True, blank=True, help_text=_("Status update message")
    )
    status_updated_at = models.DateTimeField(
        null=True, blank=True, help_text=_("Last status update timestamp")
    )
    views_count = models.PositiveIntegerField(default=0, help_text=_("Number of views"))
    rental_count = models.PositiveIntegerField(
        default=0, help_text=_("Number of rentals")
    )
    average_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_("Average rating (0-5)"),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["category"]),
            models.Index(fields=["product_type"]),
        ]
        verbose_name = _("Product")
        verbose_name_plural = _("Products")

    def __str__(self):
        return self.title

    def increment_views(self):
        self.views_count = models.F("views_count") + 1
        self.save(update_fields=["views_count"])

    def increment_rentals(self):
        self.rental_count = models.F("rental_count") + 1
        self.save(update_fields=["rental_count"])

    def update_average_rating(self, rating):
        total_rating = models.F("average_rating") * models.F("rental_count")
        total_rating += rating
        self.average_rating = total_rating / (models.F("rental_count") + 1)
        self.save(update_fields=["average_rating"])

    def get_average_rating(self):
        return self.average_rating if self.average_rating else 0

    def is_date_available(self, date):
        return not self.unavailable_periods.filter(
            models.Q(
                models.Q(is_range=False, single_date=date)
                | models.Q(is_range=True, range_start__lte=date, range_end__gte=date)
            )
        ).exists()

    def update_status(self, new_status, message=None):
        self.status = new_status
        self.status_message = message
        self.status_updated_at = timezone.now()
        self.save(update_fields=["status", "status_message", "status_updated_at"])
