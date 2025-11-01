from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session, joinedload
from core.database import get_db
from core.dependencies import get_current_user, get_current_admin_user
from schemas.order import Order, OrderCreate, OrderUpdate, OrderSummary
from models.user import User
from models.order import Order as OrderModel, OrderItem as OrderItemModel
from decimal import Decimal
from services.recommendation_service import RecommendationService
import uuid

router = APIRouter()

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_order(
    order_data: OrderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new order."""
    # Minimal implementation: persist Order and OrderItems to DB and return created Order
    try:
        # compute total amount
        total = Decimal('0.00')
        items = []
        for it in order_data.items:
            quantity = int(it.quantity)
            unit_price = Decimal(str(it.unit_price))
            subtotal = unit_price * quantity
            total += subtotal
            items.append({
                'book_id': str(it.book_id),
                'quantity': quantity,
                'unit_price': unit_price,
                'subtotal': subtotal
            })

        order = OrderModel(
            user_id=current_user.id,
            shipping_address=order_data.shipping_address,
            payment_method=order_data.payment_method,
            total_amount=total
        )

        db.add(order)
        db.flush()  # assign order.id

        # create order items
        for it in items:
            oi = OrderItemModel(
                order_id=order.id,
                book_id=it['book_id'],
                quantity=it['quantity'],
                unit_price=it['unit_price'],
                subtotal=it['subtotal']
            )
            db.add(oi)

        db.commit()
        db.refresh(order)

        # record PURCHASE interactions for recommender
        try:
            recomm_service = RecommendationService()
            for it in items:
                recomm_service.record_interaction(str(current_user.id), it['book_id'], 'PURCHASE', db)
        except Exception:
            # non-fatal if recording fails
            pass

        return order

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/{order_id}", response_model=Order)
async def get_order(
    order_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get order by ID."""
    try:
        order_uuid = uuid.UUID(order_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid order ID format")
    
    order = db.query(OrderModel).options(
        joinedload(OrderModel.items).joinedload(OrderItemModel.book)
    ).filter(OrderModel.id == order_uuid).first()
    
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    # Only owner or admin can fetch (admin check via dependency elsewhere)
    if str(order.user_id) != str(current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this order")

    return order

@router.get("/", response_model=list[OrderSummary])
async def get_orders(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's orders."""
    orders = (
        db.query(OrderModel)
        .filter(OrderModel.user_id == current_user.id)
        .order_by(OrderModel.created_at.desc())
        .all()
    )

    result = []
    for o in orders:
        result.append({
            'id': str(o.id),
            'status': o.status,
            'total_amount': float(o.total_amount),
            'created_at': o.created_at,
            'items_count': len(o.items) if o.items is not None else 0
        })

    return result

@router.put("/{order_id}/status", response_model=Order)
async def update_order_status(
    order_id: str,
    order_data: OrderUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Update order status (admin only)."""
    # TODO: Implement order service
    return {"message": f"Order {order_id} status updated"}

@router.post("/{order_id}/payment")
async def process_payment(
    order_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Process order payment."""
    # TODO: Implement payment service
    return {"message": f"Payment processed for order {order_id}"}
