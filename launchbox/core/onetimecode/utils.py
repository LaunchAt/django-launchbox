import base64
from datetime import datetime
from uuid import UUID

import pyotp


def uuid_to_base32_code(uuid: UUID) -> str:
    """Get the Base32 encoded string of the UUID.

    Args:
        uuid (UUID): The UUID to be converted.

    Returns:
        str: The Base32 encoded string of the UUID.
    """
    return base64.b32encode(uuid.bytes).decode('utf-8').rstrip('=')


def generate_otp(secret_key: str, time: datetime) -> str:
    """Generate a six-digit code as a One Time Password (OTP).

    Args:
        secret_key (str): The secret key used to generate the code.
        time (datetime): The datetime at which the code is generated.

    Returns:
        str: The six-digit code as a One Time Password (OTP).
    """
    totp = pyotp.TOTP(secret_key)
    return totp.generate_otp(totp.timecode(time))
