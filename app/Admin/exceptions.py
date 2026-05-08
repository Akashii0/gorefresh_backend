from app.common.exceptions import NotFound


class AdminNotFound(NotFound):
    """
    Exception for 404 Admin Not Found
    """

    def __init__(self, *, loc: list | None = None):
        super().__init__("Admin Not Found", loc=loc)
