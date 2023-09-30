import phonenumbers

from .settings import DEFAULT_COUNTRY_CODE


def parse_phone_number(value: str) -> phonenumbers.PhoneNumber:
    """Parse the input phone number and return a PhoneNumber object.

    Args:
        value (str): The input phone number as a string.

    Returns:
        phonenumbers.PhoneNumber: A PhoneNumber object
            representing the parsed number.

    Raises:
        phonenumbers.NumberParseException: If the input phone number is
            not a valid phone number or if it cannot be parsed. If the
            DEFAULT_COUNTRY_CODE is None, and the phone number's format
            is valid, but no country code is provided.
    """
    return phonenumbers.parse(value, DEFAULT_COUNTRY_CODE)


def format_phone_number(phonenumber_obj: phonenumbers.PhoneNumber) -> str:
    """Format the given PhoneNumber object as an E.164 formatted phone
    number.

    Args:
        phonenumber_obj (phonenumbers.PhoneNumber): The PhoneNumber object
            to format.

    Returns:
        str: The formatted phone number as an E.164 string.
    """
    return phonenumbers.format_number(
        phonenumber_obj,
        phonenumbers.PhoneNumberFormat.E164,
    )


def normalize_phone_number(value: str) -> str:
    """Normalize the input phone number string by parsing and
    formatting it.

    Args:
        value (str): The input phone number as a string.

    Returns:
        str: The normalized phone number as an E.164 string.

    Raises:
        phonenumbers.NumberParseException: If the input phone number is
            not a valid phone number or if it cannot be parsed. If the
            DEFAULT_COUNTRY_CODE is None, and the phone number's format
            is valid, but no country code is provided.
    """
    parsed_number = parse_phone_number(value)
    return format_phone_number(parsed_number)
