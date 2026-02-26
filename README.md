📦 Ecommerce Backend (Django + DRF + Docker)

A production-ready ecommerce backend built with:

Django & Django REST Framework

PostgreSQL (Multi-Database Setup)

Redis

Celery (Background Tasks + Celery Beat)

Docker & Docker Compose

Separate HTML/CSS/Vanilla JS frontend

🚀 Features

Custom User Model

Multi-database architecture

Product & Category management

Cart & Orders

Reviews system

Redis caching

Celery background jobs

Periodic scheduled tasks

Django Admin

Dockerized setup

🏗 Project Architecture
Client (Frontend)
        ↓
Django REST API (Gunicorn)
        ↓
PostgreSQL (users + store_db)
        ↓
Redis (cache + broker + result backend)
        ↓
Celery Worker + Celery Beat
🐳 Run With Docker (Recommended)
1️⃣ Clone Repository
git clone https://github.com/yourusername/ecommerce.git
cd ecommerce
2️⃣ Setup Environment Variables

Copy template:

cp .env.example .env

Fill values inside .env.

3️⃣ Build & Start Containers
docker compose build
docker compose up
4️⃣ Create Databases (First Time Only)
docker compose exec db psql -U postgres

Inside psql:

CREATE DATABASE ecommerce_users_db;
CREATE DATABASE ecommerce_store_db;
\q
5️⃣ Run Migrations
docker compose exec web python manage.py migrate
docker compose exec web python manage.py migrate --database=store_db
6️⃣ Create Superuser
docker compose exec web python manage.py createsuperuser
7️⃣ Access Application

Admin:

http://localhost:8000/admin/

API:

http://localhost:8000/api/
🧪 Load Sample Data (Optional)

If you have fixtures:

docker compose exec web python manage.py loaddata default_data.json
docker compose exec web python manage.py loaddata store_data.json --database=store_db
🔁 Reset Database (Development)
docker compose down -v
docker compose up
⚙️ Environment Variables

Example .env.example:

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

⚠ Never commit your real .env file.

🧵 Celery Commands

Test task manually:

docker compose exec web python manage.py shell
from store.tasks import deactivate_unsold_products
deactivate_unsold_products.delay()
📂 Tech Stack
Component	Technology
Backend	Django + DRF
Database	PostgreSQL
Cache	Redis
Background Jobs	Celery
Scheduler	Celery Beat
Server	Gunicorn
Containerization	Docker
📦 Services
Service	Description
web	Django + Gunicorn
db	PostgreSQL
redis	Redis server
celery	Celery worker
celery-beat	Scheduled tasks
🔐 Security Notes

Do not expose .env

Rotate SECRET_KEY in production

Disable DEBUG in production

Use strong database passwords

🛠 Development Notes

Restart celery after modifying tasks:

docker compose restart celery

Rebuild only if requirements.txt changes:

docker compose build --no-cache

👨‍💻 Author

Savan Paradava
