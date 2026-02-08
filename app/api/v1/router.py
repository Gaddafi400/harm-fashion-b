"""API v1 router"""
from fastapi import APIRouter

from app.api.v1.endpoints import auth, customers, orders, payments, measurements, settings, users

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(users.router)

api_router.include_router(customers.router)
api_router.include_router(orders.router)
api_router.include_router(payments.router)
api_router.include_router(measurements.router)

api_router.include_router(settings.router, prefix="/settings")
