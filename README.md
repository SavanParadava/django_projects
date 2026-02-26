# 🚀 Ecommerce Backend

### Django + DRF + Docker

A **production-ready ecommerce backend** built with modern backend
architecture and scalable services.

------------------------------------------------------------------------

## 🛠 Tech Stack

-   🐍 **Django + Django REST Framework**
-   🐘 **PostgreSQL (Multi-Database Setup)**
-   ⚡ **Redis (Cache + Broker + Result Backend)**
-   🔄 **Celery + Celery Beat (Background & Scheduled Tasks)**
-   🐳 **Docker & Docker Compose**
-   🌐 **HTML / CSS / Vanilla JavaScript Frontend**
-   🔫 **Gunicorn**

------------------------------------------------------------------------

## ✨ Features

-   👤 Custom User Model\
-   🔐 Role-Based Access (Admin / Retailer / Customer)\
-   🗄 Multi-database architecture\
-   📦 Product & Category Management\
-   🛒 Cart & Order System\
-   ⭐ Reviews System\
-   🔎 Dynamic Filtering, Search & Pagination\
-   🛡 Custom Middleware (Rate Limiting + Validation)\
-   ⚡ Redis Caching\
-   🤖 Background Jobs (Automatic Product Delisting)\
-   ⏰ Periodic Scheduled Tasks\
-   🧑‍💼 Django Admin Panel\
-   🐳 Fully Dockerized Setup

------------------------------------------------------------------------

## 🏗 Project Architecture

    Client (Frontend)
            ↓
    Django REST API (Gunicorn)
            ↓
    PostgreSQL (users_db + store_db)
            ↓
    Redis (cache + broker + result backend)
            ↓
    Celery Worker + Celery Beat

------------------------------------------------------------------------

# 🐳 Run With Docker

## 1️⃣ Clone Repository

``` bash
git clone https://github.com/yourusername/ecommerce.git
cd ecommerce
```

## 2️⃣ Setup Environment Variables

``` bash
cp .env.example .env
```

Fill the required values inside `.env`.

------------------------------------------------------------------------

## 3️⃣ Build & Start Containers

``` bash
docker compose build
docker compose up
```

------------------------------------------------------------------------

## 4️⃣ Create Databases (First Time Only)

``` bash
docker compose exec db psql -U postgres
```

Inside psql:

``` sql
CREATE DATABASE ecommerce_users_db;
CREATE DATABASE ecommerce_store_db;
\q
```

------------------------------------------------------------------------

## 5️⃣ Run Migrations

``` bash
docker compose exec web python manage.py migrate
docker compose exec web python manage.py migrate --database=store_db
```

------------------------------------------------------------------------

## 6️⃣ Create Superuser

``` bash
docker compose exec web python manage.py createsuperuser
```

------------------------------------------------------------------------

## 7️⃣ Start Frontend Server

``` bash
python -m http.server 5500
```

------------------------------------------------------------------------

## 🌐 Access Application

  Service       URL
  ------------- ------------------------------
-   Admin Panel   http://localhost:8000/admin/
-   API           http://localhost:8000/api/
-   Frontend      http://localhost:5500

------------------------------------------------------------------------

# 📥 Load Sample Data (Optional)

``` bash
docker compose exec web python manage.py loaddata default_data.json
docker compose exec web python manage.py loaddata store_data.json --database=store_db
```

------------------------------------------------------------------------

# 🔄 Reset Database (Development)

``` bash
docker compose down -v
docker compose up
```

------------------------------------------------------------------------

# 🧪 Celery Test Command

``` bash
docker compose exec web python manage.py shell
```

Inside shell:

``` python
from store.tasks import deactivate_unsold_products
deactivate_unsold_products.delay()
```

------------------------------------------------------------------------

# 🧩 Services Overview

  Service       Description
  ------------- -------------------
-   web           Django + Gunicorn
-   db            PostgreSQL
-   redis         Redis Server
-   celery        Celery Worker
-   celery-beat   Scheduled Tasks

------------------------------------------------------------------------

# 🔐 Security Notes

-   ❌ Do NOT expose `.env`
-   🔑 Rotate `SECRET_KEY` in production
-   🛑 Disable `DEBUG` in production
-   🔒 Use strong database passwords

------------------------------------------------------------------------

# 🧑‍💻 Development Notes

Restart Celery after modifying tasks:

``` bash
docker compose restart celery
```

Rebuild only if `requirements.txt` changes:

``` bash
docker compose build --no-cache
```

------------------------------------------------------------------------

# 👨‍💻 Author

**Savan Paradava**
