from app.common.exceptions import NotFound


class OrderNotFound(NotFound):
    """
    Exception for 404 order not found
    """

    def __init__(self, *, loc: list | None = None):
        super().__init__("Order not found", loc=loc)


class OrderItemNotFound(NotFound):
    """
    Exception for 404 order item not found
    """

    def __init__(self, *, loc: list | None = None):
        super().__init__("Order item not found", loc=loc)
