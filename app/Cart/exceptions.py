from app.common.exceptions import NotFound


class CartNotFound(NotFound):
    """
    Exception for 404 Cart not found
    """

    def __init__(self, *, loc: list | None = None):
        super().__init__("Cart not found", loc=loc)


class CartProductNotFound(NotFound):
    """
    Exception for 404 Cart product not found
    """

    def __init__(self, *, loc: list | None = None):
        super().__init__("Cart product not found", loc=loc)
