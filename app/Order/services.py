import base64
import random
import string
from datetime import datetime, time, timedelta, timezone
from decimal import Decimal
from io import BytesIO
from pathlib import Path
from typing import cast

from jinja2 import Environment, FileSystemLoader
from sqlalchemy.ext.asyncio import AsyncSession
from xhtml2pdf import pisa

from app.Cart import models as cart_models
from app.Cart import selectors as cart_selectors
from app.Cart import services as cart_services
from app.Cart.exceptions import CartNotFound
from app.Cart.selectors import get_cart_by_id
from app.common.exceptions import BadRequest
from app.core.settings import get_settings
from app.external.brevo.client import BrevoClient
from app.external.brevo.schemas import BrevoAttachment, BrevoEmailPayload

# from app.coupon import selectors as coupon_selectors
from app.external.paystack.client import InternalPaystackClient
from app.Order import models, selectors
from app.Order.crud import OrderCRUD, OrderItemCRUD
from app.Order.schemas import create
# from app.User import models as user_models

# Globals
settings = get_settings()
TEMPLATES_DIR = Path(__file__).resolve().parents[2] / "templates"
env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))


async def create_order_from_cart(
    *, user_id: int, data: create.CartOrderCreate, db: AsyncSession
):
    """
    Create order obj

    Args:
        data (create.CartOrderCreate): The order details
        db (AsyncSession): The database session

    Raises:
        BadRequest: "Cannot create order from empty cart"
        BadRequest: "Invalid total order amount"
        CartNotFound

    Returns:
        models.Order
    """

    # Initialize CRUDs
    order_crud = OrderCRUD(db=db)
    order_item_crud = OrderItemCRUD(db=db)

    # Get cart with related products
    cart = cast(cart_models.Cart, await get_cart_by_id(id=data.cart_id, db=db))

    if not cart:
        raise CartNotFound()

    if cart.user_id != user_id:
        raise BadRequest("You are not authorized to create this order")

    if not cart.products:
        raise BadRequest("Cannot create order from empty cart")

    delivery_fee = Decimal("1000.00")
    subtotal = Decimal("0.00")

    # Create base order
    order = await order_crud.create(
        data={
            "order_ref": _generate_order_ref(),
            "user_id": user_id,
            "cart_id": cart.id,
            "payment_status": "Pending",
            "status": "Pending",
            "delivery_fee": float(delivery_fee),
            "estimated_delivery_time": _calculate_estimated_delivery_time().strftime(
                "%H:%M:%S"
            ),
            "created_at": datetime.now(timezone.utc),
            **data.model_dump(exclude={"cart_id"}),
        }
    )

    # Add products
    if cart.products:
        for cart_product in cart.products:
            unit_price = Decimal(str(cart_product.product.price))
            item_total = unit_price * cart_product.quantity
            subtotal += Decimal(str(item_total))

            await order_item_crud.create(
                data={
                    "order_id": order.id,
                    "product_id": cart_product.product_id,
                    "quantity": cart_product.quantity,
                    "unit_price": float(unit_price),
                }
            )

    # calculate the service fee i.e 2.5%
    SERVICE_FEE_PERCENT = Decimal("2.5")
    service_fee = (subtotal * SERVICE_FEE_PERCENT) / 100

    # Apply coupon discount if provided
    discount_amount = Decimal("0.0")
    # coupon_id = None

    # if data.coupon_code:
    #     try:
    #         coupon = await coupon_selectors.get_coupon_by_code(
    #             code=data.coupon_code, db=db, raise_exc=True
    #         )

    #         # Check if coupon is active
    #         if not coupon.is_active:
    #             raise BadRequest("Coupon is not active")

    #         # Calculate discount based on discount_type
    #         discount_percentage = Decimal(str(coupon.discount_percentage))

    #         if coupon.discount_type == "food_total":
    #             # Apply discount to subtotal
    #             discount_amount = (subtotal * discount_percentage) / 100
    #         elif coupon.discount_type == "delivery_fee":
    #             # Apply discount to delivery fee
    #             discount_amount = (delivery_fee * discount_percentage) / 100

    #         coupon_id = coupon.id

    #     except Exception as e:
    #         if isinstance(e, BadRequest):
    #             raise
    #         raise BadRequest(f"Invalid or inactive coupon code: {data.coupon_code}")

    # Compute total and update
    total = subtotal + delivery_fee + service_fee - discount_amount
    if total <= 0:  # type: ignore
        raise BadRequest("Invalid total order amount")

    setattr(order, "service_fee", float(service_fee))
    setattr(order, "subtotal", float(subtotal))
    setattr(order, "discount_amount", float(discount_amount))
    # setattr(order, "coupon_id", coupon_id)
    setattr(order, "total_amount", float(total))

    await db.commit()
    await db.refresh(order)

    return order


# ! DEPRECATED
async def generate_order_invoice_pdf(order: models.Order):
    """
    ! DEPRECATED
    Generates a PDF invoice for the given order ID.

    Returns:
        Path to the generated PDF file.
    """
    TEMPLATES_DIR = Path(__file__).resolve().parent.parent.parent / "templates"
    LOGO_PATH = TEMPLATES_DIR / "saharaLogo.png"

    # Encode image to base64
    with open(LOGO_PATH, "rb") as image_file:
        logo_base64 = base64.b64encode(image_file.read()).decode("utf-8")

    order_dict = {
        "id": order.id,
        "order_ref": order.order_ref,
        "created_at": order.created_at,
        "email": order.user.email,
        "full_name": f"{order.user.first_name} {order.user.last_name}",
        "phone_number": order.user.phone,
        "delivery_address": order.delivery_address,
        "payment_method": order.payment_method,
        "subtotal": float(order.subtotal),  # type: ignore
        "service_fee": float(order.service_fee),  # type: ignore
        "delivery_fee": float(order.delivery_fee),  # type: ignore
        "total_amount": float(order.total_amount),  # type: ignore
        "products": [
            {
                "name": item.product.name,
                "quantity": item.quantity,
                "unit_price": float(item.unit_price),  # type: ignore
            }
            for item in order.order_items
        ],
    }

    # Jinja2 template render
    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template("invoice.html")
    # Render HTML with Jinja2
    html_out = template.render(order=order_dict, logo_base64=logo_base64)

    # Output path
    output_path = TEMPLATES_DIR / f"invoice_order_{order.order_ref}.pdf"

    # Generate PDF
    with open(output_path, "wb") as file:
        pisa_status = pisa.CreatePDF(html_out, dest=file)

    if pisa_status.err:  # type: ignore
        raise RuntimeError("Failed to generate invoice PDF.")

    return output_path


async def init_paystack_payment(user_email: str, order: models.Order, db: AsyncSession):
    """
    Initiate a Paystack transaction for an order.

    Args:
        order (models.Order): The Order obj

    Returns:
        The Paystack payment data
    """
    # Init Paystack client
    paystack_client = InternalPaystackClient()

    callback_url = f"{settings.PAYSTACK_CALLBACK_BASE_URL}"

    response = await paystack_client.init_transaction(
        amount=float(order.total_amount * 100),  # type: ignore
        email=user_email,  # type: ignore
        callback_url=callback_url,
        metadata={"order_ref": order.order_ref},
    )

    setattr(order, "paystack_reference", response.data.reference)
    setattr(order, "paystack_token", response.data.access_code)

    await db.commit()

    return response


async def verify_order_payment(reference: str, db: AsyncSession):
    """
    Verifies a Paystack transaction and updates the order

    Args:
        reference (str): The paystack transaction reference
        db (AsyncSession): The database session

    Returns:
        models.Order: The updated Order
    """
    # Init Paystack client
    paystack_client = InternalPaystackClient()

    response = await paystack_client.verify_transaction(reference=reference)
    ref = response.data.reference
    order = await selectors.get_order_by_ref(id=ref, db=db)
    if response.data.status == "success":
        setattr(order, "payment_status", "Paid")
        setattr(order, "payment_method", f"{response.data.channel}")
        setattr(order, "status", "Confirmed")
        setattr(order, "updated_at", datetime.now(timezone.utc))

        await admin_order_email(order=order)
        await user_order_email(order=order)

        if order.cart_id:  # type: ignore
            cart = await cart_selectors.get_cart_by_id(id=order.cart_id, db=db)  # type: ignore
            await cart_services.delete_cart(cart=cart, db=db)

        await db.commit()
        await db.refresh(order)
    elif response.data.status == "failed":
        setattr(order, "payment_status", "Failed")
        setattr(order, "payment_method", f"{response.data.channel}")
        setattr(order, "status", "Cancelled")
        setattr(order, "updated_at", datetime.now(timezone.utc))

        await db.commit()
        await db.refresh(order)
    else:
        setattr(order, "payment_status", "Pending")
        setattr(order, "payment_method", f"{response.data.channel}")
        setattr(order, "status", "Pending")
        setattr(order, "updated_at", datetime.now(timezone.utc))

    return response


async def verify_payment(reference: str, db: AsyncSession):
    """
    Verifies a Paystack transaction and updates the order

    Args:
        reference (str): The paystack transaction reference
        db (AsyncSession): The database session

    Returns:
        models.Order: The updated Order
    """
    # Init Paystack client
    paystack_client = InternalPaystackClient()

    response = await paystack_client.verify_transaction(reference=reference)
    ref = response.data.reference
    order = await selectors.get_order_by_ref(id=ref, db=db)
    if response.data.status == "success":
        setattr(order, "payment_status", "Paid")
        setattr(order, "payment_method", f"{response.data.channel}")
        setattr(order, "status", "Confirmed")
        setattr(order, "updated_at", datetime.now(timezone.utc))

        await db.commit()
        await db.refresh(order)
    elif response.data.status == "failed":
        setattr(order, "payment_status", "Failed")
        setattr(order, "payment_method", f"{response.data.channel}")
        setattr(order, "status", "Cancelled")
        setattr(order, "updated_at", datetime.now(timezone.utc))

        await db.commit()
        await db.refresh(order)
    else:
        setattr(order, "payment_status", "Pending")
        setattr(order, "payment_method", f"{response.data.channel}")
        setattr(order, "status", "Pending")
        setattr(order, "updated_at", datetime.now(timezone.utc))

    return response


async def admin_order_email(order: models.Order):
    """
    Alert an admin of an order

    Args:
        order (models.Order): The order obj

    Returns:
        The email response
    """
    brevo_client = BrevoClient()

    pdf: bytes = await _generate_order_invoice_pdf_bytes(order=order)

    attachments = [
        BrevoAttachment(
            name=f"invoice_order_{order.order_ref}.pdf",
            content=base64.b64encode(pdf).decode(),
        )
    ]

    html = await _render_admin_email_template(order=order)

    param = BrevoEmailPayload(
        sender={
            "name": settings.DEFAULT_SENDER_NAME,  # e.g., "GoRefresh Admin"
            "email": settings.DEFAULT_SENDER_EMAIL,  # e.g., "no-reply@gorefresh.com"
        },  # type: ignore
        to=[{"email": settings.ADMIN_EMAIL}],
        subject=f"New Order Received — [Order #{order.id}]",
        textContent="New order ready for processing. Please see the attached invoice.",
        htmlContent=html,
        attachment=attachments,
    )

    await brevo_client.send_email(param)

    return "Email sent successfully"


async def user_order_email(order: models.Order):
    """
    Alert an user of an order

    Args:
        order (models.Order): The order obj

    Returns:
        The email response
    """
    brevo_client = BrevoClient()

    pdf: bytes = await _generate_order_invoice_pdf_bytes(order=order)

    attachments = [
        BrevoAttachment(
            name=f"invoice_order_{order.order_ref}.pdf",
            content=base64.b64encode(pdf).decode(),
        )
    ]

    html = await _render_user_email_template(order=order)

    param = BrevoEmailPayload(
        sender={
            "name": settings.DEFAULT_SENDER_NAME,  # e.g., "GoRefresh Support"
            "email": settings.DEFAULT_SENDER_EMAIL,
        },  # type: ignore
        to=[{"email": order.user.email}],
        subject="Thank You for choosing Gorefresh!",
        htmlContent=html,
        attachment=attachments,
    )

    await brevo_client.send_email(param)

    return "Email sent successfully"


def _calculate_estimated_delivery_time() -> time:
    """Calculate realistic delivery time"""
    return (datetime.now(timezone.utc) + timedelta(minutes=45)).time()


def _generate_order_ref(length=8):
    """
    Generate a random order_ref
    """
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=length))


async def _generate_order_invoice_pdf_bytes(order: models.Order) -> bytes:
    """
    Generates a PDF invoice for the given order.

    Returns:
        PDF file as bytes.
    """
    TEMPLATES_DIR = Path(__file__).resolve().parent.parent.parent / "templates"
    LOGO_PATH = TEMPLATES_DIR / "gorefresh_logo.png"

    # Encode image to base64
    with open(LOGO_PATH, "rb") as image_file:
        logo_base64 = base64.b64encode(image_file.read()).decode("utf-8")

    order_dict = {
        "id": order.id,
        "order_ref": order.order_ref,
        "created_at": order.created_at,
        "email": order.user.email,
        "full_name": f"{order.user.first_name} {order.user.last_name}",
        "phone_number": order.user.phone,
        "delivery_address": order.delivery_address,
        "payment_method": order.payment_method,
        "subtotal": float(order.subtotal),  # type: ignore
        "service_fee": float(order.service_fee),  # type: ignore
        "delivery_fee": float(order.delivery_fee),  # type: ignore
        "total_amount": float(order.total_amount),  # type: ignore
        "products": [
            {
                "name": item.product.name,
                "quantity": item.quantity,
                "unit_price": float(item.unit_price),  # type: ignore
            }
            for item in order.order_items
        ],
    }

    # Render HTML with Jinja2
    env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))
    template = env.get_template("invoice.html")
    html_out = template.render(order=order_dict, logo_base64=logo_base64)

    # Generate PDF in memory
    pdf_buffer = BytesIO()
    pisa_status = pisa.CreatePDF(html_out, dest=pdf_buffer)

    if pisa_status.err:  # type: ignore
        raise RuntimeError("Failed to generate invoice PDF.")

    return pdf_buffer.getvalue()


async def _render_admin_email_template(order: models.Order) -> str:
    """
    Render the admin email HTML template with order data using Jinja2.
    """
    # Build items list as string
    items_str = "\n".join(
        f"- {item.product.name} x{item.quantity} @ ₦{float(item.unit_price)}"  # type: ignore
        for item in order.order_items
    )

    # Load the template
    template = env.get_template("admin-email.html")

    # Render with values
    html_content = template.render(
        order_id=order.id,
        # restaurant_name=order.restaurant.name,
        customer_name=f"{order.user.first_name} {order.user.last_name}",
        delivery_address=order.delivery_address,
        delivery_instructions=order.additional_info or "—",
        contact_number=order.user.phone,
        items_ordered=items_str,
        total_amount=order.total_amount,
    )

    return html_content


async def _render_user_email_template(order: models.Order) -> str:
    """
    Render the user email HTML template with order data using Jinja2.
    """
    # Load the template
    template = env.get_template("user-email.html")

    # Render with values
    html_content = template.render(
        full_name=f"{order.user.first_name} {order.user.last_name}",
        order_ref=order.paystack_reference,
    )

    return html_content
