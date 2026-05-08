from functools import lru_cache
from pydantic import BaseModel


class RouteTags(BaseModel):
    """
    Base model for app route tags
    """

    # User Module
    USER: str = "User Endpoints"

    # admin tags
    ADMIN: str = "Admin Endpoints"

    # product tags
    PRODUCT: str = "Product Endpoints"
    PRODUCT_CATEGORY: str = "Product Category"
    PRODUCT_IMAGE: str = "Product Image"


@lru_cache
def get_tags():
    """
    Returns the app RouteTags
    """
    return RouteTags()
