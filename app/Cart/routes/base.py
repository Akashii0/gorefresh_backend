from typing import cast

from fastapi import APIRouter

from app.Cart import models as cart_models
from app.Cart import selectors, services
from app.Cart.exceptions import CartNotFound
from app.Cart.formatters import format_cart
from app.Cart.schemas import create, edit, response
from app.User.annotations import CurrentUser
from app.common.annotations import DatabaseSession
from app.common.schemas import ResponseSchema
from app.core.settings import get_settings

# Globals
router = APIRouter()
settings = get_settings()


@router.post(
    "",
    summary="Create a cart",
    response_description="The created cart's details",
    status_code=200,
    response_model=response.CartResponse,
)
async def route_cart_create(
    cart_in: create.CartCreate, curr_user: CurrentUser, db: DatabaseSession
):
    """
    This endpoint creates a cart
    """

    # Create the cart
    cart = await services.create_cart(data=cart_in, user_id=curr_user.id, db=db)

    # Format and return the cart
    return {"data": await format_cart(cart=cart)}


@router.get(
    "/me",
    summary="Return an existing cart for a user",
    response_description="The retrieved cart's details",
    status_code=200,
    response_model=ResponseSchema,
)
async def route_fetch_user_cart(curr_user: CurrentUser, db: DatabaseSession):
    """
    This endpoint fetches a user's cart items
    """

    cart = await selectors.get_cart_by_user_id(user_id=curr_user.id, db=db)

    if not cart:
        raise CartNotFound()

    return {"msg": "Cart cleared successfully.", "data": await format_cart(cart=cart)}


@router.get(
    "/{cart_id}",
    summary="Fetch a cart",
    response_description="The fetched cart's details",
    status_code=200,
    response_model=response.CartResponse,
)
async def route_cart_fetch(cart_id: int, db: DatabaseSession):
    """
    This endpoint fetches a cart
    """

    # Fetch the cart
    cart = cast(cart_models.Cart, await selectors.get_cart_by_id(id=cart_id, db=db))

    # Format and return the cart
    return {"data": await format_cart(cart=cart)}


@router.get(
    "/{cart_id}/total",
    summary="Fetch a cart's Total",
    response_description="The fetched cart's total",
    status_code=200,
    response_model=ResponseSchema,
)
async def route_cart_fetch_total(cart_id: int, db: DatabaseSession):
    """
    This endpoint fetches a cart's total
    """

    # Fetch the cart
    cart = cast(cart_models.Cart, await selectors.get_cart_by_id(id=cart_id, db=db))

    # Format and return the cart
    return {
        "msg": "cart's total retrieved successfully",
        "data": {"total": cart.total_amount},
    }


@router.post(
    "/{cart_id}/add",
    summary="Add product to an existing cart",
    response_description="The updated cart with added product",
    status_code=200,
    response_model=response.CartResponse,
)
async def route_cart_add_product(
    cart_id: int,
    curr_user: CurrentUser,
    item_in: create.CartProductBulkCreate,
    db: DatabaseSession,
):
    """
    This endpoint adds products to an existing cart.
    """

    # Add item to cart
    cart = await services.add_product_to_cart(
        cart_id=cart_id, user_id=curr_user.id, data=item_in, db=db
    )

    # Return formatted cart
    return {"data": await format_cart(cart=cart)}


@router.put(
    "/{cart_id}/edit",
    summary="Edit product quantity of an existing cart",
    response_description="The updated cart with editted product",
    status_code=200,
    response_model=response.CartResponse,
)
async def route_cart_edit_product_quantity(
    cart_id: int,
    item_in: edit.CartProductEdit,
    db: DatabaseSession,
):
    """
    This endpoint edits food item of an existing cart.
    """

    # edit item in cart
    cart = await services.update_product_quantity_in_cart(
        cart_id=cart_id, data=item_in, db=db
    )

    # Return formatted cart
    return {"data": await format_cart(cart=cart)}


@router.delete(
    "/{cart_id}/remove",
    summary="Remove product from an existing cart",
    response_description="The updated cart with removed product",
    status_code=200,
    response_model=response.CartResponse,
)
async def route_cart_remove_product(
    cart_id: int,
    curr_user: CurrentUser,
    product_id: int,
    db: DatabaseSession,
):
    """
    This endpoint removes a food item from an existing cart.
    """

    # Remove item from cart
    cart = await services.remove_product_from_cart(
        cart_id=cart_id, user_id=curr_user.id, product_id=product_id, db=db
    )

    # Return formatted cart
    return {"data": await format_cart(cart=cart)}


@router.delete(
    "/{cart_id}/clear",
    summary="Clear an existing cart",
    response_description="The cleared cart's details",
    status_code=200,
    response_model=ResponseSchema,
)
async def route_clear_cart(cart_id: int, curr_user: CurrentUser, db: DatabaseSession):
    """
    This endpoint clears a cart's items
    """

    cart = await services.clear_cart(cart_id=cart_id, user_id=curr_user.id, db=db)

    return {"msg": "Cart cleared successfully.", "data": await format_cart(cart=cart)}
