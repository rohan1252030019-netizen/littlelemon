from django.shortcuts import render
from rest_framework import generics, status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from django_filters.rest_framework import DjangoFilterBackend

from .models import Booking, MenuItem
from .permissions import IsOwnerOrManager, ReadOnlyOrManager, is_manager
from .serializers import (
    BookingSerializer,
    MenuItemSerializer,
    RegistrationSerializer,
    UserSerializer,
)


# ---------------------------------------------------------------------------
# Server-rendered pages
# ---------------------------------------------------------------------------


def home(request):
    """Landing page with the featured dishes."""
    featured_items = MenuItem.objects.filter(featured=True)[:3]
    return render(
        request,
        "index.html",
        {"featured_items": featured_items, "menu_count": MenuItem.objects.count()},
    )


def menu_page(request):
    """Menu page rendered from the database with Django templates."""
    return render(request, "menu.html", {"menu_items": MenuItem.objects.all()})


# ---------------------------------------------------------------------------
# Menu API
# ---------------------------------------------------------------------------


class MenuItemViewSet(viewsets.ModelViewSet):
    """
    list:   GET    /api/menu/            (public)
    create: POST   /api/menu/            (Manager)
    read:   GET    /api/menu/{id}/       (public)
    update: PUT    /api/menu/{id}/       (Manager)
    patch:  PATCH  /api/menu/{id}/       (Manager)
    delete: DELETE /api/menu/{id}/       (Manager)
    """

    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [ReadOnlyOrManager]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["category", "featured"]
    search_fields = ["title", "description"]
    ordering_fields = ["title", "price", "inventory", "created_at"]
    ordering = ["title"]


# ---------------------------------------------------------------------------
# Booking API
# ---------------------------------------------------------------------------


class BookingViewSet(viewsets.ModelViewSet):
    """
    list:   GET    /api/bookings/        (authenticated; own bookings, or all for Manager)
    create: POST   /api/bookings/        (authenticated)
    read:   GET    /api/bookings/{id}/   (owner or Manager)
    update: PUT    /api/bookings/{id}/   (owner or Manager)
    delete: DELETE /api/bookings/{id}/   (owner or Manager)
    """

    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrManager]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["booking_date", "no_of_guests"]
    ordering_fields = ["booking_date", "no_of_guests", "created_at"]
    ordering = ["-booking_date"]

    def get_queryset(self):
        user = self.request.user
        queryset = Booking.objects.select_related("user")
        if is_manager(user):
            return queryset
        return queryset.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# ---------------------------------------------------------------------------
# Authentication API
# ---------------------------------------------------------------------------


class RegistrationView(generics.CreateAPIView):
    """POST /api/registration/ - create an account and return an auth token."""

    serializer_class = RegistrationSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        return Response(
            {"user": UserSerializer(user).data, "token": token.key},
            status=status.HTTP_201_CREATED,
        )


class TokenLoginView(ObtainAuthToken):
    """POST /api/auth/token/login/ - exchange username/password for a token."""

    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, _ = Token.objects.get_or_create(user=user)
        return Response(
            {
                "token": token.key,
                "user_id": user.pk,
                "username": user.username,
            }
        )


class LogoutView(generics.GenericAPIView):
    """POST /api/auth/token/logout/ - revoke the current user's token."""

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        Token.objects.filter(user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class MeView(generics.RetrieveAPIView):
    """GET /api/auth/users/me/ - profile of the authenticated user."""

    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user
