import tempfile
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Request
from fastapi.responses import FileResponse, JSONResponse


from app.User.annotations import CurrentUser
from app.common.annotations import DatabaseSession
from app.common.exceptions import BadRequest
from app.common.schemas import ResponseSchema
from app.core.settings import get_settings
from app.Order import selectors, services
from app.Order.schemas import create

# Globals
router = APIRouter()
settings = get_settings()


@router.post(
    "",
    summary="Create an Order from a cart",
    response_description="The created order's details",
    status_code=200,
    response_model=ResponseSchema,
)
async def route_cart_order_create(
    curr_user: CurrentUser, order_in: create.CartOrderCreate, db: DatabaseSession
):
    """
    This endpoint creates an order from a cart
    """

    # Create the order
    order = await services.create_order_from_cart(
        user_id=curr_user.id, data=order_in, db=db
    )
    payment_url = await services.init_paystack_payment(
        user_email=curr_user.email, order=order, db=db
    )

    return {
        "msg": "Order created successfully",
        "data": payment_url,
    }


@router.post(
    "/{reference}/verify",
    summary="Verify an order's status",
    response_description="The verification data",
    status_code=200,
    response_model=ResponseSchema,
)
async def route_verify_payment(
    reference: str,
    db: DatabaseSession,
):
    """
    Paystack callback route to verify transaction
    """
    order_verif = await services.verify_order_payment(reference=reference, db=db)

    return {**order_verif.model_dump()}


@router.post(
    "/webhook/paystack",
    summary="Webhook listener for verification status",
    response_description="Successfully received verification status",
    status_code=200,
)
async def route_paystack_method(
    request: Request,
    background_tasks: BackgroundTasks,
    db: DatabaseSession,
):
    """
    Paystack webhook listener
    """
    payload = await request.json()
    event = payload.get("event")
    data = payload.get("data")

    if event in ["charge.success", "charge.failed", "charge.abandoned"]:
        reference = data.get("reference")

        await services.verify_payment(reference=reference, db=db)

        # Run verification in background
        background_tasks.add_task(services.verify_order_payment, reference, db)

    return JSONResponse(content={"status": "received successfully"}, status_code=200)


@router.get(
    "/{order_ref}/invoice",
    summary="PDF Receipt generator for orders",
    response_description="The pdf receipt of the order",
    status_code=200,
    response_class=FileResponse,
)
async def route_download_order_receipt(order_ref: str, db: DatabaseSession):
    """
    This endpoint generates a pdf receipt for an order
    """
    order = await selectors.get_order_by_ref(id=order_ref, db=db)

    if order.payment_status != "Paid":  # type: ignore
        raise BadRequest(msg="This order has not been paid yet. Please contact support")

    pdf: bytes = await services._generate_order_invoice_pdf_bytes(order=order)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(pdf)
        tmp_path = Path(tmp_file.name)

    return FileResponse(
        path=tmp_path,
        filename=f"invoice_order_{order.order_ref}.pdf",  # type: ignore
        media_type="application/pdf",
    )
