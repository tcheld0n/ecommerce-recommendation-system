from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from core.database import get_db
from core.dependencies import get_current_user
from schemas.cart import Cart as CartSchema, CartItemCreate, CartItemUpdate
from models.user import User
from models.cart import Cart, CartItem
from models.book import Book
from decimal import Decimal

router = APIRouter()


def _serialize_cart(cart: Cart) -> CartSchema:
    # Build Cart schema from SQLAlchemy models
    items = []
    total_items = 0
    total_amount = Decimal('0')

    for item in cart.items:
        book = item.book
        unit_price = getattr(book, 'price', Decimal('0'))
        subtotal = (unit_price or Decimal('0')) * item.quantity
        total_items += item.quantity
        total_amount += subtotal

        items.append({
            'id': item.id,
            'book_id': item.book_id,
            'quantity': item.quantity,
            'created_at': item.created_at,
            'updated_at': item.updated_at,
            'book': {
                'id': book.id,
                'title': book.title,
                'author': book.author,
                'price': book.price,
                'cover_image_url': book.cover_image_url,
            },
            'unit_price': unit_price,
            'subtotal': subtotal,
        })

    return CartSchema(
        id=cart.id,
        user_id=cart.user_id,
        items=items,
        total_items=total_items,
        total_amount=total_amount,
        created_at=cart.created_at,
        updated_at=cart.updated_at,
    )


def _get_or_create_cart(db: Session, user_id):
    cart = db.query(Cart).options(joinedload(Cart.items).joinedload(CartItem.book)).filter(Cart.user_id == user_id).first()
    if not cart:
        cart = Cart(user_id=user_id)
        db.add(cart)
        db.commit()
        db.refresh(cart)
    return cart


@router.get("/", response_model=CartSchema)
async def get_cart(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's cart."""
    cart = _get_or_create_cart(db, current_user.id)
    # ensure items are loaded
    cart = db.query(Cart).options(joinedload(Cart.items).joinedload(CartItem.book)).filter(Cart.id == cart.id).first()
    return _serialize_cart(cart)


@router.post("/items", response_model=CartSchema)
async def add_to_cart(
    item_data: CartItemCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add item to cart."""
    # validate book exists
    book = db.query(Book).filter(Book.id == item_data.book_id).first()
    if not book:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")

    cart = _get_or_create_cart(db, current_user.id)

    # check if item exists
    existing = db.query(CartItem).filter(CartItem.cart_id == cart.id, CartItem.book_id == item_data.book_id).first()
    if existing:
        existing.quantity = existing.quantity + item_data.quantity
    else:
        existing = CartItem(cart_id=cart.id, book_id=item_data.book_id, quantity=item_data.quantity)
        db.add(existing)

    db.commit()
    db.refresh(cart)

    cart = db.query(Cart).options(joinedload(Cart.items).joinedload(CartItem.book)).filter(Cart.id == cart.id).first()
    return _serialize_cart(cart)


@router.put("/items/{item_id}", response_model=CartSchema)
async def update_cart_item(
    item_id: str,
    item_data: CartItemUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update cart item quantity."""
    item = db.query(CartItem).join(Cart).filter(CartItem.id == item_id, Cart.user_id == current_user.id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart item not found")

    if item_data.quantity <= 0:
        db.delete(item)
    else:
        item.quantity = item_data.quantity

    db.commit()

    cart = db.query(Cart).options(joinedload(Cart.items).joinedload(CartItem.book)).filter(Cart.id == item.cart_id).first()
    return _serialize_cart(cart)


@router.delete("/items/{item_id}")
async def remove_from_cart(
    item_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove item from cart."""
    item = db.query(CartItem).join(Cart).filter(CartItem.id == item_id, Cart.user_id == current_user.id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart item not found")

    db.delete(item)
    db.commit()
    return {"detail": "Item removed"}


@router.delete("/")
async def clear_cart(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Clear cart."""
    cart = db.query(Cart).filter(Cart.user_id == current_user.id).first()
    if not cart:
        return {"detail": "Cart already empty"}

    # delete items
    db.query(CartItem).filter(CartItem.cart_id == cart.id).delete()
    db.commit()
    return {"detail": "Cart cleared"}
