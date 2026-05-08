from app.common.exceptions import NotFound


class ProductCategoryNotFound(NotFound):
    """
    Exception for 404 Product category not found
    """

    def __init__(self, *, loc: list | None = None):
        super().__init__("Product category not found", loc=loc)


class ProductNotFound(NotFound):
    """
    Exception for 404 Product item not found
    """

    def __init__(self, *, loc: list | None = None):
        super().__init__("Product item not found", loc=loc)
