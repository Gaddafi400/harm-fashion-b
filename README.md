# Tailoring Order Management System - Backend

FastAPI backend for the Tailoring Order Management System.

## Setup

1. Create virtual environment: `python -m venv venv`
2. Activate: `source venv/bin/activate` (Windows: `venv\Scripts\activate`)
3. Install dependencies: `pip install -r requirements.txt`
4. Configure: `cp .env.example .env` and edit with your settings
5. Create database: `createdb tailoring_db`
6. Run migrations: `alembic upgrade head`
7. Create admin: `python create_admin.py`
8. Run server: `uvicorn app.main:app --reload`

## API Documentation
- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

## Default Credentials
Username: admin
Password: admin123
# harm-fashion-b
