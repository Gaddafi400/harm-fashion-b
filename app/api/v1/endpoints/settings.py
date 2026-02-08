from fastapi import APIRouter

router = APIRouter(tags=["Settings"])

APP_SETTINGS = {
    "business_name": " HAAM FASHION",
    "currency_code": "XOF",
    "currency_symbol": "CFA",
    "currency_position": "BEFORE",
    "measurement_unit": "cm",
    "date_format": "YYYY-MM-DD",
    "business_phone": "+1234567890",
    "business_email": "info@mytailoring.com",
    "business_address": "123 Main Street, City, Country"
}


@router.get("/")
async def get_settings():
    """Get the app settings"""
    return APP_SETTINGS
