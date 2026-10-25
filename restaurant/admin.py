from django.contrib import admin

from .models import Booking, MenuItem


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "price", "inventory", "featured")
    list_filter = ("category", "featured")
    search_fields = ("title", "description")
    list_editable = ("price", "inventory", "featured")


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("name", "no_of_guests", "booking_date", "user")
    list_filter = ("booking_date",)
    search_fields = ("name", "user__username")
    date_hierarchy = "booking_date"
