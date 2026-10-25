from django.urls import include, path
from rest_framework.permissions import AllowAny
from rest_framework.routers import APIRootView, DefaultRouter

from . import views


class PublicAPIRootView(APIRootView):
    """Make /api/ browsable without logging in first."""

    permission_classes = [AllowAny]


class LittleLemonRouter(DefaultRouter):
    APIRootView = PublicAPIRootView


router = LittleLemonRouter()
router.register("menu", views.MenuItemViewSet, basename="menu")
router.register("bookings", views.BookingViewSet, basename="booking")

urlpatterns = [
    path("", include(router.urls)),
    path("registration/", views.RegistrationView.as_view(), name="registration"),
    path("auth/token/login/", views.TokenLoginView.as_view(), name="token-login"),
    path("auth/token/logout/", views.LogoutView.as_view(), name="token-logout"),
    path("auth/users/me/", views.MeView.as_view(), name="users-me"),
]
