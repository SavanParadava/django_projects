# Ecommerce Backend (Django + DRF + Docker)

A production-ready ecommerce backend built with:

-   Django & Django REST Framework
-   PostgreSQL (Multi-Database Setup)
-   Redis
-   Celery (Background Tasks + Celery Beat)
-   Docker & Docker Compose
-   Separate HTML / CSS / Vanilla JavaScript frontend

## Features

-   Custom User Model
-   Multi-database architecture
-   Product & Category management
-   Cart & Orders system
-   Reviews system
-   Redis caching
-   Celery background jobs
-   Periodic scheduled tasks (Celery Beat)
-   Django Admin
-   Fully Dockerized setup

## Project Architecture

    Client (Frontend)
            ↓
    Django REST API (Gunicorn)
            ↓
    PostgreSQL (users_db + store_db)
            ↓
    Redis (cache + broker + result backend)
            ↓
    Celery Worker + Celery Beat

## Run With Docker

### 1. Clone Repository

``` bash
git clone https://github.com/yourusername/ecommerce.git
cd ecommerce
```

### 2. Setup Environment Variables

``` bash
cp .env.example .env
```

Fill values inside `.env`.

### 3. Build & Start Containers

``` bash
docker compose build
docker compose up
```

### 4. Create Databases (First Time Only)

``` bash
docker compose exec db psql -U postgres
```

Inside psql:

``` sql
CREATE DATABASE ecommerce_users_db;
CREATE DATABASE ecommerce_store_db;
\q
```

### 5. Run Migrations

``` bash
docker compose exec web python manage.py migrate
docker compose exec web python manage.py migrate --database=store_db
```

### 6. Create Superuser

``` bash
docker compose exec web python manage.py createsuperuser
```

### 7. Access Application

Admin Panel:\
http://localhost:8000/admin/

API:\
http://localhost:8000/api/

## Load Sample Data (Optional)

``` bash
docker compose exec web python manage.py loaddata default_data.json
docker compose exec web python manage.py loaddata store_data.json --database=store_db
```

## Reset Database (Development)

``` bash
docker compose down -v
docker compose up
```

## Environment Variables (.env.example)

``` env
DEBUG=True
SECRET_KEY=change-me

POSTGRES_DB_USERS=
POSTGRES_DB_STORE=
POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_HOST=db
POSTGRES_PORT=5432

REDIS_URL=redis://redis:6379/1
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/2
```

Never commit your real `.env` file.

## Celery Test Command

``` bash
docker compose exec web python manage.py shell
```

``` python
from store.tasks import deactivate_unsold_products
deactivate_unsold_products.delay()
```

## Tech Stack

-   Backend: Django + DRF
-   Database: PostgreSQL
-   Cache: Redis
-   Background Jobs: Celery
-   Scheduler: Celery Beat
-   Server: Gunicorn
-   Containerization: Docker

## Services

-   web --- Django + Gunicorn
-   db --- PostgreSQL
-   redis --- Redis server
-   celery --- Celery worker
-   celery-beat --- Scheduled tasks

## Security Notes

-   Do not expose `.env`
-   Rotate `SECRET_KEY` in production
-   Disable `DEBUG` in production
-   Use strong database passwords

## Development Notes

Restart Celery after modifying tasks:

``` bash
docker compose restart celery
```

Rebuild only if `requirements.txt` changes:

``` bash
docker compose build --no-cache
```

## Author

Savan Paradava
