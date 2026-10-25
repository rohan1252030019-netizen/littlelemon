from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class MenuItem(models.Model):
    """A dish or drink that Little Lemon serves."""

    class Category(models.TextChoices):
        STARTER = "starter", "Starter"
        MAIN = "main", "Main course"
        DESSERT = "dessert", "Dessert"
        DRINK = "drink", "Drink"

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    inventory = models.SmallIntegerField(
        default=0, validators=[MinValueValidator(0)]
    )
    category = models.CharField(
        max_length=20, choices=Category.choices, default=Category.MAIN
    )
    featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["title"]
        verbose_name = "menu item"
        verbose_name_plural = "menu items"

    def __str__(self) -> str:
        return f"{self.title} : {self.price}"


class Booking(models.Model):
    """A table reservation made by a Little Lemon customer."""

    name = models.CharField(max_length=255)
    no_of_guests = models.SmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(20)]
    )
    booking_date = models.DateTimeField()
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="bookings",
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-booking_date"]
        verbose_name = "booking"
        verbose_name_plural = "bookings"

    def __str__(self) -> str:
        return f"{self.name} - {self.no_of_guests} guests on {self.booking_date:%Y-%m-%d %H:%M}"
