import phonenumbers


def paginate_list(items: list, page: int, size: int):
    """
    Paginate list

    Args:
        items (list): The list of items
        page (int): The page
        size (int): The size

    Returns:
        list
    """
    # Calculate start and end indices
    start = (page - 1) * size
    end = start + size

    # Return the sliced list
    return items[start:end] if start < len(items) else []


def validate_phone_number(phone_number: str) -> bool:
    """
    Validate the phone number using the phonenumbers library

    Args:
        phone_number (str): The phone number to validate

    Returns:
        bool: True if the phone number is valid, False otherwise
    """
    # Parse the phone number
    try:
        phonenumbers.parse(phone_number, None)
    except phonenumbers.NumberParseException:
        return False

    return True
