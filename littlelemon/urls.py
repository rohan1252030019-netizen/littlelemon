"""
URL configuration for the Little Lemon project.

HTML pages are served by Django at the root of the site, while the REST API
lives under /api/.
"""

from django.contrib import admin
from django.urls import include, path

from restaurant import views

urlpatterns = [
    path("admin/", admin.site.urls),
    # Server-rendered pages
    path("", views.home, name="home"),
    path("menu/", views.menu_page, name="menu-page"),
    # REST API
    path("api/", include("restaurant.urls")),
]
