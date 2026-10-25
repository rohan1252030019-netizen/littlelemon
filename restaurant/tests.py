"""Unit tests for the Little Lemon restaurant API."""

from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from .models import Booking, MenuItem

User = get_user_model()
PASSWORD = "Str0ngPass!2026"


def future(days: int = 2):
    """Return an aware datetime a few days in the future."""
    return timezone.now() + timedelta(days=days)


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------


class MenuItemModelTests(TestCase):
    def test_str_contains_title_and_price(self):
        item = MenuItem.objects.create(title="Greek Salad", price=Decimal("12.99"))
        self.assertEqual(str(item), "Greek Salad : 12.99")

    def test_default_category_is_main_course(self):
        item = MenuItem.objects.create(title="Moussaka", price=Decimal("18.00"))
        self.assertEqual(item.category, MenuItem.Category.MAIN)

    def test_negative_inventory_is_invalid(self):
        item = MenuItem(title="Soup", price=Decimal("5.00"), inventory=-1)
        with self.assertRaises(ValidationError):
            item.full_clean()


class BookingModelTests(TestCase):
    def test_str_contains_name_and_guests(self):
        booking = Booking.objects.create(
            name="Ada", no_of_guests=4, booking_date=future(3)
        )
        self.assertIn("Ada", str(booking))
        self.assertIn("4 guests", str(booking))

    def test_zero_guests_is_invalid(self):
        booking = Booking(name="Ada", no_of_guests=0, booking_date=future(3))
        with self.assertRaises(ValidationError):
            booking.full_clean()

    def test_more_than_twenty_guests_is_invalid(self):
        booking = Booking(name="Ada", no_of_guests=21, booking_date=future(3))
        with self.assertRaises(ValidationError):
            booking.full_clean()


# ---------------------------------------------------------------------------
# Shared API fixtures
# ---------------------------------------------------------------------------


class RestaurantAPITestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.manager_group = Group.objects.create(name="Manager")

        cls.manager = User.objects.create_user(
            "manager", email="manager@example.com", password=PASSWORD
        )
        cls.manager.groups.add(cls.manager_group)
        cls.customer = User.objects.create_user(
            "customer", email="customer@example.com", password=PASSWORD
        )
        cls.other = User.objects.create_user(
            "other", email="other@example.com", password=PASSWORD
        )

        cls.salad = MenuItem.objects.create(
            title="Greek Salad",
            description="Lettuce, feta and olives",
            price=Decimal("12.99"),
            inventory=25,
            category=MenuItem.Category.STARTER,
            featured=True,
        )
        cls.fish = MenuItem.objects.create(
            title="Grilled Fish",
            description="Catch of the day",
            price=Decimal("24.50"),
            inventory=10,
            category=MenuItem.Category.MAIN,
        )
        cls.booking = Booking.objects.create(
            name="Customer booking",
            no_of_guests=2,
            booking_date=future(3),
            user=cls.customer,
        )

    def authenticate(self, user):
        self.client.force_authenticate(user=user)


# ---------------------------------------------------------------------------
# Menu API
# ---------------------------------------------------------------------------


class MenuAPITests(RestaurantAPITestCase):
    def test_anonymous_user_can_list_menu(self):
        response = self.client.get(reverse("menu-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]["title"], "Greek Salad")

    def test_menu_can_be_searched(self):
        response = self.client.get(reverse("menu-list"), {"search": "fish"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], "Grilled Fish")

    def test_menu_can_be_filtered_by_category(self):
        response = self.client.get(reverse("menu-list"), {"category": "starter"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], "Greek Salad")

    def test_menu_can_be_ordered_by_price(self):
        response = self.client.get(reverse("menu-list"), {"ordering": "price"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["title"], "Greek Salad")

    def test_anonymous_user_cannot_create_menu_item(self):
        response = self.client.post(
            reverse("menu-list"),
            {"title": "Hummus", "price": "6.00", "inventory": 10},
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_customer_cannot_create_menu_item(self):
        self.authenticate(self.customer)

        response = self.client.post(
            reverse("menu-list"),
            {"title": "Hummus", "price": "6.00", "inventory": 10},
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(MenuItem.objects.filter(title="Hummus").exists())

    def test_manager_can_create_menu_item(self):
        self.authenticate(self.manager)

        response = self.client.post(
            reverse("menu-list"),
            {
                "title": "Hummus",
                "description": "Chickpea dip",
                "price": "6.00",
                "inventory": 10,
                "category": "starter",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(MenuItem.objects.filter(title="Hummus").exists())

    def test_anonymous_user_can_retrieve_menu_item(self):
        response = self.client.get(reverse("menu-detail", args=[self.salad.id]))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["price"], "12.99")

    def test_manager_can_update_menu_item(self):
        self.authenticate(self.manager)

        response = self.client.put(
            reverse("menu-detail", args=[self.salad.id]),
            {
                "title": "Greek Salad",
                "description": "Updated description",
                "price": "13.50",
                "inventory": 20,
                "category": "starter",
                "featured": True,
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.salad.refresh_from_db()
        self.assertEqual(self.salad.price, Decimal("13.50"))

    def test_manager_can_delete_menu_item(self):
        self.authenticate(self.manager)

        response = self.client.delete(reverse("menu-detail", args=[self.fish.id]))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(MenuItem.objects.filter(pk=self.fish.pk).exists())

    def test_customer_cannot_delete_menu_item(self):
        self.authenticate(self.customer)

        response = self.client.delete(reverse("menu-detail", args=[self.fish.id]))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(MenuItem.objects.filter(pk=self.fish.pk).exists())


# ---------------------------------------------------------------------------
# Booking API
# ---------------------------------------------------------------------------


class BookingAPITests(RestaurantAPITestCase):
    def test_anonymous_user_cannot_list_bookings(self):
        response = self.client.get(reverse("booking-list"))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_user_can_create_booking(self):
        self.authenticate(self.customer)

        response = self.client.post(
            reverse("booking-list"),
            {
                "name": "Dinner for two",
                "no_of_guests": 2,
                "booking_date": future(5).isoformat(),
            },
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        booking = Booking.objects.get(pk=response.data["id"])
        self.assertEqual(booking.user, self.customer)
        self.assertEqual(response.data["user"], "customer")

    def test_user_only_sees_their_own_bookings(self):
        Booking.objects.create(
            name="Other booking",
            no_of_guests=3,
            booking_date=future(4),
            user=self.other,
        )
        self.authenticate(self.customer)

        response = self.client.get(reverse("booking-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], self.booking.name)

    def test_manager_sees_every_booking(self):
        Booking.objects.create(
            name="Other booking",
            no_of_guests=3,
            booking_date=future(4),
            user=self.other,
        )
        self.authenticate(self.manager)

        response = self.client.get(reverse("booking-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_user_cannot_read_another_users_booking(self):
        self.authenticate(self.other)

        response = self.client.get(reverse("booking-detail", args=[self.booking.id]))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_owner_can_update_booking(self):
        self.authenticate(self.customer)

        response = self.client.patch(
            reverse("booking-detail", args=[self.booking.id]),
            {"no_of_guests": 6},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.no_of_guests, 6)

    def test_user_cannot_delete_another_users_booking(self):
        self.authenticate(self.other)

        response = self.client.delete(
            reverse("booking-detail", args=[self.booking.id])
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Booking.objects.filter(pk=self.booking.pk).exists())

    def test_manager_can_delete_any_booking(self):
        self.authenticate(self.manager)

        response = self.client.delete(
            reverse("booking-detail", args=[self.booking.id])
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Booking.objects.filter(pk=self.booking.pk).exists())

    def test_booking_in_the_past_is_rejected(self):
        self.authenticate(self.customer)

        response = self.client.post(
            reverse("booking-list"),
            {
                "name": "Yesterday",
                "no_of_guests": 2,
                "booking_date": (timezone.now() - timedelta(days=1)).isoformat(),
            },
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("booking_date", response.data)

    def test_booking_with_zero_guests_is_rejected(self):
        self.authenticate(self.customer)

        response = self.client.post(
            reverse("booking-list"),
            {
                "name": "Nobody",
                "no_of_guests": 0,
                "booking_date": future(6).isoformat(),
            },
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("no_of_guests", response.data)


# ---------------------------------------------------------------------------
# Registration and authentication
# ---------------------------------------------------------------------------


class AuthAPITests(RestaurantAPITestCase):
    def test_registration_creates_user_and_returns_token(self):
        response = self.client.post(
            reverse("registration"),
            {
                "username": "newuser",
                "email": "new@example.com",
                "password": PASSWORD,
                "password2": PASSWORD,
            },
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username="newuser").exists())
        self.assertIn("token", response.data)
        self.assertEqual(response.data["user"]["username"], "newuser")
        self.assertEqual(response.data["user"]["groups"], [])

    def test_registration_rejects_duplicate_username(self):
        response = self.client.post(
            reverse("registration"),
            {"username": "customer", "password": PASSWORD, "password2": PASSWORD},
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("username", response.data)

    def test_registration_rejects_weak_password(self):
        response = self.client.post(
            reverse("registration"),
            {"username": "weakuser", "password": "12345678", "password2": "12345678"},
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)

    def test_registration_rejects_mismatched_passwords(self):
        response = self.client.post(
            reverse("registration"),
            {
                "username": "mismatch",
                "password": PASSWORD,
                "password2": "DifferentPass!2026",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password2", response.data)

    def test_token_login_returns_a_token(self):
        response = self.client.post(
            reverse("token-login"),
            {"username": "customer", "password": PASSWORD},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.data)
        self.assertTrue(Token.objects.filter(user=self.customer).exists())

    def test_token_login_rejects_bad_credentials(self):
        response = self.client.post(
            reverse("token-login"),
            {"username": "customer", "password": "wrong-password"},
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn("token", response.data)

    def test_token_can_be_used_to_access_protected_endpoints(self):
        token = Token.objects.create(user=self.customer)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")

        response = self.client.get(reverse("booking-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_me_endpoint_returns_the_authenticated_user(self):
        self.authenticate(self.customer)

        response = self.client.get(reverse("users-me"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "customer")

    def test_me_endpoint_requires_authentication(self):
        response = self.client.get(reverse("users-me"))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_revokes_the_token(self):
        token = Token.objects.create(user=self.customer)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")

        logout_response = self.client.post(reverse("token-logout"))
        me_response = self.client.get(reverse("users-me"))

        self.assertEqual(logout_response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Token.objects.filter(user=self.customer).exists())
        self.assertEqual(me_response.status_code, status.HTTP_401_UNAUTHORIZED)


# ---------------------------------------------------------------------------
# Server-rendered pages and API index
# ---------------------------------------------------------------------------


class StaticPageTests(RestaurantAPITestCase):
    def test_home_page_is_served_by_django(self):
        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTemplateUsed(response, "index.html")
        self.assertContains(response, "Little Lemon")
        self.assertContains(response, "Greek Salad")

    def test_menu_page_lists_database_items(self):
        response = self.client.get(reverse("menu-page"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTemplateUsed(response, "menu.html")
        self.assertContains(response, "Grilled Fish")
        self.assertContains(response, "24.50")

    def test_api_root_is_available(self):
        response = self.client.get("/api/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("menu", response.data)
        self.assertIn("bookings", response.data)
