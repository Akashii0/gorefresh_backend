from datetime import datetime, timezone
from decimal import Decimal
from typing import cast

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.Cart import models
from app.Cart.crud import CartCRUD, CartProductCRUD
from app.Cart.exceptions import CartNotFound
from app.Cart.schemas import create, edit
from app.Cart.selectors import get_cart_by_id, get_cart_by_user_id
from app.common.exceptions import BadRequest
from app.Product.exceptions import ProductNotFound

# from app.Product import models as product_model
from app.Product.selectors import get_products_by_ids

# from app.Product.utils import is_product_available_today


# Constants as Decimal
SERVICE_FEE_PERCENT = Decimal("2.5")  # 2.5%
DEFAULT_DELIVERY_FEE = Decimal("1000")  # to be dynamic later


async def create_cart(
    *,
    data: create.CartCreate,
    user_id: int,
    db: AsyncSession,
) -> models.Cart:
    """
    Create a cart with optional initial products.
    """

    # Enforce one cart per user
    existing_cart = await get_cart_by_user_id(user_id, db, raise_exc=False)
    if existing_cart:
        raise BadRequest(
            "User already has an active cart. Use that cart instead of creating a new one."
        )

    cart_crud = CartCRUD(db=db)
    cart_product_crud = CartProductCRUD(db=db)

    # 1. Validate and batch load products in one query
    product_ids = {item.product_id for item in data.products}  # i used set to dedupe
    products = await get_products_by_ids(list(product_ids), db)
    products_map = {p.id: p for p in products}

    missing = product_ids - products_map.keys()
    if missing:
        raise ProductNotFound(f"Products not found: {missing}")

    # 2. Calculate totals (all Decimal)
    subtotal = Decimal("0")
    cart_items_data = []
    for item in data.products:
        product = products_map[item.product_id]
        item_total = product.price * item.quantity
        subtotal += item_total
        cart_items_data.append(
            {
                "product_id": item.product_id,
                "quantity": item.quantity,
                "unit_price": product.price,
            }
        )

    service_fee = (subtotal * SERVICE_FEE_PERCENT) / Decimal("100")
    total = subtotal + DEFAULT_DELIVERY_FEE + service_fee

    if total <= 0:
        raise BadRequest("Invalid order total calculated.")

    # 3. Create cart (no commit yet)
    cart = await cart_crud.create(
        data={
            "user_id": user_id,
            "delivery_fee": DEFAULT_DELIVERY_FEE,
            "service_fee": service_fee,
            "subtotal": subtotal,
            "total_amount": total,
            "created_at": datetime.now(timezone.utc),
        },
        commit=False,
    )

    # Force flush to generate cart.id
    await db.flush()

    # 4. Bulk insert cart items
    if cart_items_data:
        bulk_data = [{"cart_id": cart.id, **item} for item in cart_items_data]
        await cart_product_crud.bulk_create(bulk_data, commit=False)

    # Single commit at the end
    await db.commit()
    await db.refresh(cart)

    return cart


async def add_product_to_cart(
    cart_id: int,
    user_id: int,
    data: create.CartProductBulkCreate,
    db: AsyncSession,
):
    """
    Add one or more products to an existing cart (atomic, with row lock).

    Args:
        cart_id (int): The ID of the cart
        data (create.CartproductCreate): The product's details
        db (AsyncSession): The database session

    Returns:
        models.Cart: The cart obj
    """
    # Init Crud
    cart_product_crud = CartProductCRUD(db=db)

    # 1. Fetch cart with row lock (FOR UPDATE) to prevent concurrent updates
    cart = await db.execute(
        select(models.Cart).where(models.Cart.id == cart_id).with_for_update()
    )
    cart = cart.scalar_one_or_none()
    if not cart:
        raise CartNotFound()
    if cart.user_id != user_id:
        raise BadRequest(f"You are not authorized to modify cart {cart_id}")

    # 2. Batch load products
    product_ids = {item.product_id for item in data.products}
    products = await get_products_by_ids(list(product_ids), db)
    products_map = {p.id: p for p in products}
    missing = product_ids - products_map.keys()
    if missing:
        raise ProductNotFound(f"Products not found: {missing}")

    # 3. Load existing cart items (optional: lock them as well)
    #    We'll handle upsert manually.
    existing_items = await cart_product_crud.get_by_cart_id(
        cart_id
    )  # assume this method exists

    subtotal = cart.subtotal  # Decimal already
    # Process each product
    for item in data.products:
        product = products_map[item.product_id]
        item_total = product.price * item.quantity
        existing = next(
            (ei for ei in existing_items if ei.product_id == item.product_id), None
        )
        if existing:
            existing.quantity += item.quantity
        else:
            await cart_product_crud.create(
                data={
                    "cart_id": cart_id,
                    "product_id": item.product_id,
                    "quantity": item.quantity,
                    "unit_price": product.price,
                },
                commit=False,
            )
        subtotal += item_total

    # 4. Recalculate totals
    service_fee = (subtotal * SERVICE_FEE_PERCENT) / Decimal("100")
    total = subtotal + cart.delivery_fee + service_fee

    cart.subtotal = subtotal
    cart.service_fee = service_fee
    cart.total_amount = total
    cart.updated_at = datetime.now(timezone.utc)

    await db.commit()
    # await db.refresh(cart)
    return cart


async def update_product_quantity_in_cart(
    cart_id: int, user_id: int, data: edit.CartProductEdit, db: AsyncSession
):
    """
    Update the quantity of a product in the cart.

    Args:
        cart_id (int): The ID of the Cart
        data (edit.CartproductEdit): _description_
        db (AsyncSession): The database session
    """

    if data.quantity < 1:
        raise BadRequest("Quantity must be atleast 1.")

    # Init Crud
    cart_product_crud = CartProductCRUD(db=db)

    cart = cast(models.Cart, await get_cart_by_id(id=cart_id, db=db))

    if not cart:
        raise CartNotFound()

    if cart.user_id != user_id:
        raise BadRequest(
            f"You are not authorized to update this cart with id: {cart_id}"
        )

    cart_item = await cart_product_crud.get_by_cart_and_product(
        cart_id=cart_id, product_id=data.product_id
    )

    if not cart_item:
        raise BadRequest("This product is not in the cart.")

    # product = cast(
    #     product_model.Product, await get_product_by_id(data.product_id, db)
    # )

    # Update quantity
    setattr(cart_item, "quantity", data.quantity)
    await db.flush()

    # Recalculate subtotal
    updated_items = cart.products
    subtotal = sum(
        Decimal(str(item.unit_price)) * item.quantity for item in updated_items
    )
    delivery_fee = Decimal(str(cart.delivery_fee))
    service_fee = (subtotal * Decimal("2.5")) / 100
    total = subtotal + delivery_fee + service_fee

    # Update cart values
    setattr(cart, "subtotal", float(subtotal))  # type: ignore
    setattr(cart, "service_fee", float(service_fee))  # type: ignore
    setattr(cart, "total_amount", float(total))  # type: ignore
    setattr(cart, "updated_at", datetime.now(timezone.utc))

    await db.commit()
    # await db.refresh(cart)

    return cart


async def remove_product_from_cart(
    cart_id: int, user_id: int, product_id: int, db: AsyncSession
):
    """
    Remove a product from cart

    Args:
        cart_id (int): The ID of the cart
        product_id (int): The ID of the product
        db (AsyncSession): The database session

    Returns:
        models.Cart: The cart obj
    """
    cart_product_crud = CartProductCRUD(db)

    cart = cast(models.Cart, await get_cart_by_id(id=cart_id, db=db))

    if not cart:
        raise CartNotFound()

    if cart.user_id != user_id:
        raise BadRequest(
            f"You are not authorized to update this cart with id: {cart_id}"
        )

    cart_product = await cart_product_crud.get_by_cart_and_product(
        cart_id=cart_id, product_id=product_id
    )
    if not cart_product:
        raise BadRequest(f"Product with ID: {product_id} not in cart")

    item_total = Decimal(str(cart_product.unit_price)) * cart_product.quantity

    # Delete the item
    await cart_product_crud.delete(cart_product)

    # Recalculate subtotal
    subtotal = Decimal(str(cart.subtotal)) - item_total
    # Ensure no negative value
    subtotal = max(subtotal, Decimal("0.00"))  # type: ignore

    SERVICE_FEE_PERCENT = Decimal("2.5")  # 2.5%

    # Recalculate service fee and total
    service_fee = (subtotal * SERVICE_FEE_PERCENT) / 100
    delivery_fee = Decimal(str(cart.delivery_fee or 0))
    total = subtotal + service_fee + delivery_fee

    # Update cart fields
    setattr(cart, "subtotal", float(subtotal))
    setattr(cart, "service_fee", float(service_fee))
    setattr(cart, "total_amount", float(total))
    setattr(cart, "updated_at", datetime.now(timezone.utc))

    await db.commit()
    await db.refresh(cart)

    return cart


async def clear_cart(cart_id: int, user_id: int, db: AsyncSession):
    """
    This function clears a cart's items

    Args:
        cart_id (int): The ID of the cart
        db (AsyncSession): The database session
    """
    # Init Crud
    cart_crud = CartCRUD(db)

    # Lock cart
    cart = await db.execute(
        select(models.Cart).where(models.Cart.id == cart_id).with_for_update()
    )
    cart = cart.scalar_one_or_none()
    if not cart:
        raise CartNotFound()
    if cart.user_id != user_id:
        raise BadRequest(f"You are not authorized to modify cart {cart_id}")

    await cart_crud.clear_cart_items(cart)

    cart.subtotal = Decimal("0")
    cart.service_fee = Decimal("0")
    cart.total_amount = Decimal("0")
    cart.updated_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(cart)
    return cart


async def delete_cart(cart: models.Cart, user_id: int, db: AsyncSession):
    """
    Permanently delete a cart (only if owned by user).

    Args:
        cart (models.Cart): _description_
        db (AsyncSession): _description_
    """
    if cart.user_id != user_id:
        raise BadRequest(
            f"You are not authorized to update this cart with id: {cart.id}"
        )

    # Init CRUD
    cart_crud = CartCRUD(db=db)

    await cart_crud.delete_cart(cart=cart)

    return True
