# Globals
from fastapi import APIRouter, File, UploadFile

from app.Admin.annotations import CurrentAdmin
from app.common.annotations import DatabaseSession
from app.common.schemas import ResponseSchema
from app.Product import services

router = APIRouter()


@router.post(
    "/{product_id}/thumbnail",
    summary="Upload a Product's image",
    response_description="The uploaded Product's image url",
    status_code=200,
    response_model=ResponseSchema,
)
async def route_extraitem_thumbnail(
    curr_admin: CurrentAdmin,
    product_id: int,
    db: DatabaseSession,
    thumbnail: UploadFile = File(...),
):
    """
    This endpoint uploads an Product's thumbnail image
    """

    # Upload the thumbnail
    image = await services.upload_product_thumbnail(
        product_id=product_id, db=db, thumbnail=thumbnail
    )

    # Format and return the extraitem
    return {
        "msg": "Thumbnail uploaded successfully",
        "data": f"Thumbnail uploaded for product id: {product_id}, Thumbnail_url: {image}",
    }
