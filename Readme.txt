Little Lemon Restaurant API
Back-End Developer Capstone - Django REST Framework + MySQL

Base URL: http://127.0.0.1:8000
Browsable API root: http://127.0.0.1:8000/api/


API PATHS TO TEST WITH INSOMNIA
===============================

Menu
----
GET     /api/menu/              Public. Supports ?search=, ?category=, ?ordering=
POST    /api/menu/              Manager token required
GET     /api/menu/{id}/         Public
PUT     /api/menu/{id}/         Manager token required
PATCH   /api/menu/{id}/         Manager token required
DELETE  /api/menu/{id}/         Manager token required

Bookings
--------
GET     /api/bookings/          Token required (own bookings, or all for a Manager)
POST    /api/bookings/          Token required
GET     /api/bookings/{id}/     Owner or Manager
PUT     /api/bookings/{id}/     Owner or Manager
PATCH   /api/bookings/{id}/     Owner or Manager
DELETE  /api/bookings/{id}/     Owner or Manager

Registration and authentication
-------------------------------
POST    /api/registration/      Public
POST    /api/auth/token/login/  Public
POST    /api/auth/token/logout/ Token required
GET     /api/auth/users/me/     Token required

HTML pages served by Django
---------------------------
GET     /                       Home page
GET     /menu/                  Menu page, rendered from the database
GET     /admin/                 Django admin


HOW TO AUTHENTICATE
===================

Step 1 - request a token:

    POST /api/auth/token/login/
    Content-Type: application/json

    {
      "username": "manager",
      "password": "LemonPass!2026"
    }

    Response: { "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b", ... }

Step 2 - send the token with every protected request:

    Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b


DEMO ACCOUNTS
=============
Created by `python manage.py seed_menu`:

    manager / LemonPass!2026   Manager group: can modify the menu, sees all bookings
    guest   / GuestPass!2026   Regular customer: can create and see only own bookings

You can also create a new account with POST /api/registration/ and use the token
returned in that response.


SAMPLE REQUESTS
===============

Create a booking:

    POST /api/bookings/
    Authorization: Token <token>
    Content-Type: application/json

    {
      "name": "Table for two",
      "no_of_guests": 2,
      "booking_date": "2026-12-31T19:30:00Z"
    }

Create a menu item (Manager only):

    POST /api/menu/
    Authorization: Token <manager-token>
    Content-Type: application/json

    {
      "title": "Hummus",
      "description": "Chickpea dip with olive oil",
      "price": "6.50",
      "inventory": 20,
      "category": "starter",
      "featured": false
    }


VALIDATION RULES
================
- booking_date must be in the future (ISO 8601 format).
- no_of_guests must be between 1 and 20.
- Menu writes require a user in the Manager group (or a staff user).


RUNNING THE PROJECT
===================
1. Create and activate a virtual environment.
2. pip install -r requirements.txt
3. Create a MySQL database and copy .env.example to .env with your credentials.
4. python manage.py migrate
5. python manage.py seed_menu
6. python manage.py runserver
7. Open http://127.0.0.1:8000/

Run the unit tests with:

    python manage.py test

See README.md for the full MySQL setup (local server or Docker).
