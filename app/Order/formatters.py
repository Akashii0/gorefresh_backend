from app.Order.models import Order, OrderItem


async def format_order(order: Order):
    """
    Formats order obj to dict
    """
    return {
        "id": order.id,
        "order_ref": order.order_ref,
        "cart_id": order.cart_id,
        "user_id": order.user_id,
        # "delivery_address_id": order.delivery_address_id,
        "delivery_address": order.delivery_address,
        "additional_info": order.additional_info,
        "delivery_fee": order.delivery_fee,
        "subtotal": order.subtotal,
        "service_fee": order.service_fee,
        "total_amount": order.total_amount,
        # "discount_amount": order.discount_amount,
        "status": order.status,
        "payment_method": order.payment_method,
        "payment_reference": order.paystack_reference,
        "payment_token": order.paystack_token,
        "payment_status": order.payment_status,
        "estimated_delivery_time": order.estimated_delivery_time,
        "actual_delivery_time": order.actual_delivery_time,
        "updated_at": order.updated_at,
        "created_at": order.created_at,
        "order_items": [
            await format_order_items(order_item) for order_item in order.order_items
        ],
    }


async def format_order_items(order_item: OrderItem):
    """
    Formats orderitems obj to dict
    """
    return {
        "id": order_item.id,
        "order_id": order_item.order_id,
        "product_id": order_item.product_id,
        "product_thumbnail": order_item.product.thumbnail_url,
        "product_name": order_item.product.name,
        "product_category": order_item.product.category.name,
        "quantity": order_item.quantity,
        "unit_price": order_item.unit_price,
        "updated_at": order_item.updated_at,
        "created_at": order_item.created_at,
    }


async def format_order_items_summary(order_item: OrderItem):
    """
    Formats orderitems obj to dict
    """
    return {
        "id": order_item.id,
        "product_id": order_item.product_id,
        "product_thumbnail": order_item.product.thumbnail_url,
        "product_name": order_item.product.name,
    }
