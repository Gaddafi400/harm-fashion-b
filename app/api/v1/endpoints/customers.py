"""Customer endpoints"""
from typing import List, Optional, Union

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.customer import Customer
from app.models.user import User
from app.schemas.customer import CustomerCreate, CustomerUpdate, CustomerResponse, PaginatedResponse

router = APIRouter(prefix="/customers", tags=["Customers"])


@router.post("/", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
async def create_customer(
        customer: CustomerCreate,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Create a new customer"""
    result = await db.execute(select(Customer).where(Customer.phone == customer.phone))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone number already registered"
        )

    db_customer = Customer(**customer.model_dump())
    db.add(db_customer)
    await db.commit()
    await db.refresh(db_customer)
    return db_customer


@router.get("/", response_model=Union[PaginatedResponse, List[CustomerResponse]])
async def get_customers(
        skip: Optional[int] = Query(None, ge=0),
        limit: Optional[int] = Query(None, ge=1, le=1000),
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Get customers - with pagination if skip/limit provided, otherwise all"""

    query = select(Customer).order_by(Customer.created_at.desc())

    if skip is not None and limit is not None:
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        customers = result.scalars().all()

        count_result = await db.execute(select(func.count(Customer.id)))
        total_count = count_result.scalar()

        return {
            "customers": customers,
            "total": total_count,
            "skip": skip,
            "limit": limit,
            "has_more": skip + len(customers) < total_count
        }
    else:
        result = await db.execute(query)
        return result.scalars().all()


# @router.get("/", response_model=List[CustomerResponse])
# async def get_customers(
#     skip: int = Query(0, ge=0),
#     limit: int = Query(100, ge=1, le=100),
#     db: AsyncSession = Depends(get_db),
#     current_user: User = Depends(get_current_user)
# ):
#     """Get all customers"""
#     result = await db.execute(
#         select(Customer).offset(skip).limit(limit).order_by(Customer.created_at.desc())
#     )
#     return result.scalars().all()

@router.get("/{customer_id}", response_model=CustomerResponse)
async def get_customer(
        customer_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Get customer by ID"""
    result = await db.execute(select(Customer).where(Customer.id == customer_id))
    customer = result.scalar_one_or_none()

    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )

    return customer


@router.put("/{customer_id}", response_model=CustomerResponse)
async def update_customer(
        customer_id: int,
        customer_update: CustomerUpdate,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Update a customer"""
    result = await db.execute(select(Customer).where(Customer.id == customer_id))
    customer = result.scalar_one_or_none()

    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )

    update_data = customer_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(customer, field, value)

    await db.commit()
    await db.refresh(customer)
    return customer
