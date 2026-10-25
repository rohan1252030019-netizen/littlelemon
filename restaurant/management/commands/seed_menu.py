"""Populate the database with the Little Lemon menu and demo accounts.

Usage:
    python manage.py seed_menu

The command is idempotent: running it twice will not create duplicates.
"""

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand

from restaurant.models import MenuItem

User = get_user_model()

MENU_ITEMS = [
    {
        "title": "Greek Salad",
        "description": "Crisp lettuce, tomatoes, olives and feta with lemon dressing.",
        "price": Decimal("12.99"),
        "inventory": 25,
        "category": MenuItem.Category.STARTER,
        "featured": True,
    },
    {
        "title": "Bruschetta",
        "description": "Grilled sourdough, marinated tomatoes, garlic and basil.",
        "price": Decimal("7.99"),
        "inventory": 30,
        "category": MenuItem.Category.STARTER,
        "featured": False,
    },
    {
        "title": "Grilled Fish",
        "description": "Fresh catch of the day with lemon, herbs and seasonal greens.",
        "price": Decimal("24.50"),
        "inventory": 12,
        "category": MenuItem.Category.MAIN,
        "featured": True,
    },
    {
        "title": "Lemon Chicken",
        "description": "Roast chicken with preserved lemon, garlic and olives.",
        "price": Decimal("19.75"),
        "inventory": 18,
        "category": MenuItem.Category.MAIN,
        "featured": False,
    },
    {
        "title": "Falafel Wrap",
        "description": "Crispy chickpea falafel, tahini and pickled vegetables.",
        "price": Decimal("11.25"),
        "inventory": 22,
        "category": MenuItem.Category.MAIN,
        "featured": False,
    },
    {
        "title": "Lemon Dessert",
        "description": "Our signature lemon cake with mascarpone cream.",
        "price": Decimal("6.50"),
        "inventory": 15,
        "category": MenuItem.Category.DESSERT,
        "featured": True,
    },
    {
        "title": "Baklava",
        "description": "Layers of filo, walnuts and honey syrup.",
        "price": Decimal("5.75"),
        "inventory": 20,
        "category": MenuItem.Category.DESSERT,
        "featured": False,
    },
    {
        "title": "Sparkling Lemonade",
        "description": "House-made lemonade with mint and a splash of soda.",
        "price": Decimal("3.50"),
        "inventory": 40,
        "category": MenuItem.Category.DRINK,
        "featured": False,
    },
]

DEMO_ACCOUNTS = [
    {
        "username": "manager",
        "password": "LemonPass!2026",
        "email": "manager@littlelemon.test",
        "first_name": "Maria",
        "last_name": "Manager",
        "group": "Manager",
    },
    {
        "username": "guest",
        "password": "GuestPass!2026",
        "email": "guest@littlelemon.test",
        "first_name": "Gary",
        "last_name": "Guest",
        "group": None,
    },
]


class Command(BaseCommand):
    help = "Create the Manager group, demo users and the Little Lemon menu."

    def handle(self, *args, **options):
        manager_group, _ = Group.objects.get_or_create(name="Manager")
        Group.objects.get_or_create(name="Delivery Crew")

        for account in DEMO_ACCOUNTS:
            user, created = User.objects.get_or_create(
                username=account["username"],
                defaults={
                    "email": account["email"],
                    "first_name": account["first_name"],
                    "last_name": account["last_name"],
                },
            )
            if created:
                user.set_password(account["password"])
                user.save()
            if account["group"]:
                user.groups.add(manager_group)

        created_count = 0
        for item in MENU_ITEMS:
            _, created = MenuItem.objects.update_or_create(
                title=item["title"], defaults=item
            )
            created_count += int(created)

        self.stdout.write(
            self.style.SUCCESS(
                f"Menu ready: {len(MENU_ITEMS)} items "
                f"({created_count} created). Demo accounts: "
                + ", ".join(
                    f"{a['username']} / {a['password']}" for a in DEMO_ACCOUNTS
                )
            )
        )
