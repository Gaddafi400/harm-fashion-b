"""Order endpoints"""
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_user, require_roles
from app.core.database import get_db
from app.models.customer import Customer
from app.models.order import Order, OrderStatus
from app.models.user import User, UserRole
from app.schemas.order import OrderCreate, OrderUpdate, OrderResponse, OrderAssign

router = APIRouter(prefix="/orders", tags=["Orders"])


def generate_order_number() -> str:
    """Generate unique order number"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"ORD-{timestamp}"


@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
        order: OrderCreate,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Create a new order"""
    # Verify customer exists
    result = await db.execute(select(Customer).where(Customer.id == order.customer_id))
    customer = result.scalar_one_or_none()
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )

    # Create order
    db_order = Order(
        order_number=generate_order_number(),
        customer_id=order.customer_id,
        total_amount=order.total_amount,
        due_date=order.due_date,
        notes=order.notes,
        created_by=current_user.id,
        status=OrderStatus.PENDING
    )

    db.add(db_order)
    await db.commit()
    await db.refresh(db_order)
    return db_order


@router.get("/", response_model=List[OrderResponse])
async def get_orders(
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=100),
        status_filter: Optional[OrderStatus] = None,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Get all orders (filtered by tailor if not admin)"""
    # query = select(Order)
    query = (
        select(Order)
        .options(
            selectinload(Order.assigned_tailor),
            selectinload(Order.customer)
        )
    )

    # Tailors only see their assigned orders
    if current_user.role == UserRole.TAILOR:
        query = query.where(Order.assigned_to == current_user.id)

    if status_filter:
        query = query.where(Order.status == status_filter)

    query = query.offset(skip).limit(limit).order_by(Order.created_at.desc())

    result = await db.execute(query)
    return result.scalars().all()


@router.get("/my-orders", response_model=List[OrderResponse])
async def get_my_orders(
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=100),
        status_filter: Optional[OrderStatus] = None,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(require_roles(["TAILOR"]))
):
    """Get orders assigned to current tailor"""
    query = (
        select(Order)
        .options(
            selectinload(Order.assigned_tailor),
            selectinload(Order.customer),
        )
        .where(Order.assigned_to == current_user.id)
        .offset(skip)
        .limit(limit)
        .order_by(Order.created_at.desc())
    )

    if status_filter:
        query = query.where(Order.status == status_filter)

    query = query.offset(skip).limit(limit).order_by(Order.created_at.desc())

    result = await db.execute(query)
    return result.scalars().all()


@router.get("/unassigned", response_model=List[OrderResponse])
async def get_unassigned_orders(
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=100),
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(require_roles(["ADMIN", "TAILOR"]))
):
    """Get unassigned orders"""
    query = select(Order).where(Order.assigned_to.is_(None))
    query = query.offset(skip).limit(limit).order_by(Order.created_at.desc())

    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
        order_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Get order by ID"""
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    # Tailors can only see their assigned orders
    if current_user.role == UserRole.TAILOR and order.assigned_to != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this order"
        )

    return order


@router.put("/{order_id}", response_model=OrderResponse)
async def update_order(
        order_id: int,
        order_update: OrderUpdate,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    """Update an order"""
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    # Tailors can only update their assigned orders (status only)
    if current_user.role == UserRole.TAILOR:
        if order.assigned_to != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this order"
            )
        # Tailors can only update status
        if order_update.status:
            order.status = order_update.status
    else:
        # Admin/Cashier can update all fields
        update_data = order_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(order, field, value)

    await db.commit()
    await db.refresh(order)
    return order


@router.post("/{order_id}/assign", response_model=OrderResponse)
async def assign_order(
        order_id: int,
        assignment: OrderAssign,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(require_roles(["ADMIN"]))
):
    """Assign order to a tailor (Admin only)"""
    result = await db.execute(
        select(Order)
        .options(
            selectinload(Order.assigned_tailor),
            selectinload(Order.customer),
        )
        .where(Order.id == order_id)
    )
    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    # Verify tailor exists if assigning
    if assignment.assigned_to:
        result = await db.execute(select(User).where(User.id == assignment.assigned_to))
        tailor = result.scalar_one_or_none()

        if not tailor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tailor not found"
            )

        if tailor.role not in [UserRole.TAILOR, UserRole.ADMIN]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User must be a TAILOR or ADMIN"
            )

    order.assigned_to = assignment.assigned_to

    # Auto-update status to IN_PROGRESS when assigned
    if assignment.assigned_to and order.status == OrderStatus.PENDING:
        order.status = OrderStatus.IN_PROGRESS

    await db.commit()
    await db.refresh(order)
    return order


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_order(
        order_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(require_roles(["ADMIN"]))
):
    """Delete an order (Admin only)"""
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    await db.delete(order)
    await db.commit()
    return None

# """Order endpoints"""
# import random
# import string
# from datetime import date
# from typing import List
#
# from fastapi import APIRouter, Depends, HTTPException, status, Query
# from sqlalchemy import select, and_
# from sqlalchemy.ext.asyncio import AsyncSession
#
# from app.api.deps import get_current_user, require_roles
# from app.core.database import get_db
# from app.models.order import Order
# from app.models.user import User
# from app.schemas.order import OrderCreate, OrderUpdate, OrderResponse
#
# router = APIRouter(prefix="/orders", tags=["Orders"])
#
#
# def generate_order_number() -> str:
#     """Generate unique order number"""
#     date_part = date.today().strftime("%Y%m%d")
#     random_part = ''.join(random.choices(string.digits, k=4))
#     return f"ORD-{date_part}-{random_part}"
#
#
# @router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
# async def create_order(
#         order: OrderCreate,
#         db: AsyncSession = Depends(get_db),
#         current_user: User = Depends(require_roles(["ADMIN", "TAILOR"]))
# ):
#     """Create a new order"""
#     order_number = generate_order_number()
#
#     while True:
#         result = await db.execute(select(Order).where(Order.order_number == order_number))
#         if not result.scalar_one_or_none():
#             break
#         order_number = generate_order_number()
#
#     db_order = Order(
#         **order.model_dump(),
#         order_number=order_number,
#         created_by=current_user.id
#     )
#     db.add(db_order)
#     await db.commit()
#     await db.refresh(db_order)
#     return db_order
#
#
# @router.get("/", response_model=List[OrderResponse])
# async def get_orders(
#         skip: int = Query(0, ge=0),
#         limit: int = Query(50, ge=1, le=100),
#         status_filter: str = Query(None),
#         customer_id: int = Query(None),
#         db: AsyncSession = Depends(get_db),
#         current_user: User = Depends(get_current_user)
# ):
#     """Get all orders"""
#     query = select(Order)
#
#     filters = []
#     if status_filter:
#         filters.append(Order.status == status_filter)
#     if customer_id:
#         filters.append(Order.customer_id == customer_id)
#
#     if filters:
#         query = query.where(and_(*filters))
#
#     query = query.offset(skip).limit(limit).order_by(Order.created_at.desc())
#     result = await db.execute(query)
#     return result.scalars().all()
#
#
# @router.get("/{order_id}", response_model=OrderResponse)
# async def get_order(
#         order_id: int,
#         db: AsyncSession = Depends(get_db),
#         current_user: User = Depends(get_current_user)
# ):
#     """Get order by ID"""
#     result = await db.execute(select(Order).where(Order.id == order_id))
#     order = result.scalar_one_or_none()
#
#     if not order:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Order not found"
#         )
#
#     return order
#
#
# @router.put("/{order_id}", response_model=OrderResponse)
# async def update_order(
#         order_id: int,
#         order_update: OrderUpdate,
#         db: AsyncSession = Depends(get_db),
#         current_user: User = Depends(require_roles(["ADMIN", "TAILOR"]))
# ):
#     """Update an order"""
#     result = await db.execute(select(Order).where(Order.id == order_id))
#     order = result.scalar_one_or_none()
#
#     if not order:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Order not found"
#         )
#
#     update_data = order_update.model_dump(exclude_unset=True)
#
#     status_value = update_data.get("status")
#     collection_date_value = update_data.get("collection_date")
#
#     if status_value == "COLLECTED":
#         if not collection_date_value:
#             update_data["collection_date"] = date.today()
#     else:
#         update_data["collection_date"] = None
#
#     for field, value in update_data.items():
#         setattr(order, field, value)
#
#     await db.commit()
#     await db.refresh(order)
#     return order
