from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone
from rest_framework import serializers

from .models import Booking, MenuItem

User = get_user_model()


class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = [
            "id",
            "title",
            "description",
            "price",
            "inventory",
            "category",
            "featured",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class BookingSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        slug_field="username", read_only=True, default=None
    )

    class Meta:
        model = Booking
        fields = ["id", "name", "no_of_guests", "booking_date", "user", "created_at"]
        read_only_fields = ["id", "user", "created_at"]

    def validate_booking_date(self, value):
        if value < timezone.now():
            raise serializers.ValidationError(
                "The booking date must be in the future."
            )
        return value


class UserSerializer(serializers.ModelSerializer):
    groups = serializers.SlugRelatedField(
        many=True, slug_field="name", read_only=True
    )

    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name", "groups"]


class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={"input_type": "password"},
    )
    password2 = serializers.CharField(
        write_only=True,
        required=False,
        style={"input_type": "password"},
    )

    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name", "password", "password2"]
        extra_kwargs = {"email": {"required": False}}

    def validate(self, attrs):
        password2 = attrs.pop("password2", None)
        if password2 is not None and password2 != attrs.get("password"):
            raise serializers.ValidationError({"password2": "Passwords do not match."})
        return attrs

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
