from app.Cart.models import Cart, CartProduct


async def format_cart(cart: Cart):
    """
    Formats cart obj to dict
    """
    return {
        "id": cart.id,
        "user_id": cart.user_id,
        "delivery_fee": cart.delivery_fee,
        "subtotal": cart.subtotal,
        "service_fee": cart.service_fee,
        "total_amount": cart.total_amount,
        "updated_at": cart.updated_at,
        "created_at": cart.created_at,
        "products": [
            await format_cart_products(cart_item) for cart_item in cart.products
        ],
    }


async def format_cart_products(cart_item: CartProduct):
    """
    Formats cart products obj to dict
    """
    return {
        "id": cart_item.id,
        "cart_id": cart_item.cart_id,
        "product_id": cart_item.product_id,
        "product_thumbnail": cart_item.product.thumbnail_url,
        "product_name": cart_item.product.name,
        "product_category": cart_item.product.category.name,
        "quantity": cart_item.quantity,
        "unit_price": cart_item.unit_price,
    }
