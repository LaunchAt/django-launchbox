import jwt as pyjwt

from .settings import JWT_SECRET_KEY


def decode_token(token: str) -> dict:
    """Decode a JWT token and return the payload as a dictionary.

    Args:
        token (str): The JWT token to be decoded.

    Returns:
        dict: The decoded payload as a dictionary.

    Raises:
        pyjwt.exceptions.ExpiredSignatureError: If the token's signature
            has expired.
        pyjwt.exceptions.PyJWTError: If any other decoding issue
            occurred.
    """
    return pyjwt.decode(token, key=JWT_SECRET_KEY, algorithms=['HS256'])


def encode_token(payload: dict) -> str:
    """Encode a dictionary payload into a JWT token.

    Args:
        payload (dict): The payload to be encoded as a JWT token.

    Returns:
        str: The encoded JWT token as a string.

    Raises:
        TypeError: If the payload is not serializable.
    """
    return pyjwt.encode(payload, JWT_SECRET_KEY, algorithm='HS256')
