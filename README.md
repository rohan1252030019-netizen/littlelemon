# Little Lemon Restaurant API

Back-end capstone project for the **Meta Back-End Developer** programme.
A Django + Django REST Framework API that powers the Little Lemon restaurant:
a menu, table bookings, user registration and token authentication, all stored
in **MySQL**.

The project also serves two server-rendered HTML pages (`/` and `/menu/`) with
Django templates, so the restaurant has a small public website in front of the
API.

---

## Features

| Requirement | Where it lives |
| --- | --- |
| Django serves static HTML | `templates/`, `static/`, `restaurant/views.py` (`home`, `menu_page`) |
| Git repository | This repository, with `Readme.txt` listing the test paths |
| Backend connected to MySQL | `littlelemon/settings.py` (`DATABASES`, MySQL engine), `docker-compose.yml` |
| Menu API | `MenuItemViewSet` — full CRUD on `/api/menu/` |
| Booking API | `BookingViewSet` — full CRUD on `/api/bookings/` |
| Registration and authentication | `/api/registration/`, `/api/auth/token/login/`, `/api/auth/token/logout/`, token auth |
| Unit tests | `restaurant/tests.py` (40 tests) |
| Insomnia-ready | `Readme.txt` lists every path, demo accounts and sample bodies |

Role-based permissions are included: members of the **Manager** group can edit
the menu and see every booking, while regular customers can only manage their
own reservations. Menu reads are public.

---

## Tech stack

- Python 3.13
- Django 5.2
- Django REST Framework 3.18
- django-filter
- MySQL 8 (via `mysqlclient`)
- Token authentication (`rest_framework.authtoken`)
- Django templates + hand-written CSS (no front-end build step)

---

## Quick start

### 1. Clone and install

```bash
git clone https://github.com/rohan1252030019-netizen/little-lemon-api.git
cd little-lemon-api
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

### 2. Start MySQL

**Option A — Docker (nothing to install, uses port 3307):**

```bash
docker compose up -d db
```

Then create `.env` from `.env.example` and set `DB_PORT=3307`.

**Option B — a MySQL server already installed locally (port 3306):**

```sql
CREATE DATABASE littlelemon CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'lemon'@'localhost' IDENTIFIED BY 'lemonpass';
GRANT ALL PRIVILEGES ON littlelemon.* TO 'lemon'@'localhost';
GRANT ALL PRIVILEGES ON test_littlelemon.* TO 'lemon'@'localhost';
FLUSH PRIVILEGES;
```

### 3. Configure the environment

```bash
copy .env.example .env      # Windows
cp .env.example .env        # macOS / Linux
```

Edit `.env` if your MySQL user, password or port differs. The file is ignored
by git.

### 4. Migrate, seed and run

```bash
python manage.py migrate
python manage.py seed_menu
python manage.py runserver
```

- Website: <http://127.0.0.1:8000/>
- Menu page: <http://127.0.0.1:8000/menu/>
- Browsable API: <http://127.0.0.1:8000/api/>
- Admin: <http://127.0.0.1:8000/admin/> (`python manage.py createsuperuser`)

### 5. Run the tests

```bash
python manage.py test
```

Tests use a separate `test_littlelemon` database, which Django creates and
drops automatically. The `lemon` user needs privileges on it — both the SQL
above and the Docker init script grant them.

---

## API reference

Base URL: `http://127.0.0.1:8000`

| Method | Path | Access | Description |
| --- | --- | --- | --- |
| GET | `/api/menu/` | Public | List the menu (search, filter, ordering) |
| POST | `/api/menu/` | Manager | Create a menu item |
| GET | `/api/menu/{id}/` | Public | Retrieve one item |
| PUT / PATCH | `/api/menu/{id}/` | Manager | Update an item |
| DELETE | `/api/menu/{id}/` | Manager | Delete an item |
| GET | `/api/bookings/` | Token | Own bookings, or all for a Manager |
| POST | `/api/bookings/` | Token | Create a booking |
| GET | `/api/bookings/{id}/` | Owner / Manager | Retrieve a booking |
| PUT / PATCH | `/api/bookings/{id}/` | Owner / Manager | Update a booking |
| DELETE | `/api/bookings/{id}/` | Owner / Manager | Cancel a booking |
| POST | `/api/registration/` | Public | Register and receive a token |
| POST | `/api/auth/token/login/` | Public | Log in and receive a token |
| POST | `/api/auth/token/logout/` | Token | Revoke the token |
| GET | `/api/auth/users/me/` | Token | Current user profile |

### Query parameters

- `/api/menu/?search=fish` — search title and description
- `/api/menu/?category=starter` — `starter`, `main`, `dessert`, `drink`
- `/api/menu/?ordering=price` — order by `title`, `price`, `inventory`, `created_at`
- `/api/bookings/?ordering=-booking_date` — order bookings
- `/api/bookings/?no_of_guests=2` — filter bookings

### Authentication flow

```http
POST /api/auth/token/login/
Content-Type: application/json

{ "username": "manager", "password": "LemonPass!2026" }
```

```json
{ "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b", "user_id": 1, "username": "manager" }
```

Send the token on every protected request:

```http
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
```

Registration returns a token immediately, so a new user can start booking
without a second call:

```http
POST /api/registration/
Content-Type: application/json

{
  "username": "ada",
  "email": "ada@example.com",
  "password": "Str0ngPass!2026",
  "password2": "Str0ngPass!2026"
}
```

### Demo accounts (after `seed_menu`)

| Username | Password | Role |
| --- | --- | --- |
| `manager` | `LemonPass!2026` | Manager: menu CRUD, all bookings |
| `guest` | `GuestPass!2026` | Customer: own bookings only |

These credentials are for local marking only — change them before any real
deployment.

---

## Testing with Insomnia

1. Create an environment with `base_url = http://127.0.0.1:8000`.
2. `POST {{base_url}}/api/auth/token/login/` with the manager credentials.
3. Add a **Bearer**/header auth of type `Token` and paste the returned key
   (header name `Authorization`, value `Token <key>`).
4. Try `GET /api/menu/`, `POST /api/bookings/`, `PUT /api/menu/1/`,
   `DELETE /api/bookings/1/`.

`Readme.txt` in the repository root contains the same list of paths with sample
request bodies.

---

## Project structure

```
littlelemon/
├── littlelemon/            # Project configuration
│   ├── settings.py         # MySQL, DRF, templates, static files
│   └── urls.py             # HTML pages + /api/ include
├── restaurant/             # The application
│   ├── models.py           # MenuItem, Booking
│   ├── serializers.py      # Menu, booking, user and registration serializers
│   ├── permissions.py      # ReadOnlyOrManager, IsOwnerOrManager
│   ├── views.py            # API viewsets, auth views, HTML views
│   ├── urls.py             # DRF router + auth routes
│   ├── admin.py            # Admin configuration
│   ├── tests.py            # 40 unit / API tests
│   └── management/commands/seed_menu.py
├── templates/              # base.html, index.html, menu.html
├── static/css/style.css
├── docker-compose.yml      # Optional MySQL 8.4 for local development
├── Readme.txt              # API paths for peer reviewers
├── requirements.txt
└── manage.py
```

---

## Design notes

- **MySQL everywhere.** `settings.py` uses `django.db.backends.mysql`; credentials
  come from `.env` so nothing sensitive is committed. `DB_ENGINE=sqlite` exists
  only as an escape hatch for a quick demo.
- **Token auth over sessions for the API.** Tokens work cleanly in Insomnia and
  other REST clients; session auth stays enabled so the browsable API and admin
  remain usable.
- **Object-level permissions.** `get_queryset()` filters bookings to the current
  user, so another customer's booking returns `404` instead of leaking data.
- **Validation.** A booking must be in the future and have 1–20 guests; prices
  and inventory are validated by the model fields.
- **No pagination** on list endpoints, to keep the responses simple to inspect
  in Insomnia. Add `DEFAULT_PAGINATION_CLASS` in `REST_FRAMEWORK` if the menu
  grows.

---

## Author

Rohan — Meta Back-End Developer capstone, 2026.
