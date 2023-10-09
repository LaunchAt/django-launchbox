from datetime import timedelta

from django.db import models
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _

from ..models import UUIDPrimaryKeyMixin
from .settings import DEFAULT_JWT_EXPIRY_SECONDS
from .utils import decode_token, encode_token


class JsonWebTokenQuerySet(models.QuerySet):
    def revoke(self) -> int:
        """Revoke all tokens in the queryset by updating their
        expiration time to now.

        Returns:
            int: The number of tokens revoked.
        """
        return super().update(expires_at=now())

    def expired_set(self) -> models.QuerySet:
        """Return a queryset containing expired token instances.

        Returns:
            QuerySet: A queryset containing expired token instances.
        """
        return self.filter(expires_at__lte=now())

    def clean_up(self) -> tuple[int, dict[str, int]]:
        """Delete expired token instances from the database.

        Returns:
            tuple: A tuple containing the number of deleted tokens and a
                dictionary with information about the deletion
                operation.
        """
        return self.expired_set().delete()

    def get_by_payload(self, payload: dict) -> 'JsonWebToken':
        """Retrieve a token instance using the payload information.

        Args:
            payload (dict): The payload information of the desired
                token.

        Returns:
            JsonWebToken: The matching token instance.
        """
        return self.get(id=payload.get('jti', ''))

    def get_by_token(self, token: str) -> 'JsonWebToken':
        """Retrieve a token instance using the provided JWT token.

        Args:
            token (str): The JWT token used to find the matching token.

        Returns:
            JsonWebToken: The matching token instance.
        """
        payload = decode_token(token)
        return self.get_by_payload(payload)


class JsonWebTokenManager(
    models.Manager.from_queryset(JsonWebTokenQuerySet),  # type: ignore
):
    def generate(
        self,
        *,
        expiration_seconds: int | None = None,
        **kwargs,
    ) -> 'JsonWebToken':
        """Generate and create a new token instance with the provided
        parameters.

        Args:
            expiration_seconds (int | None): The number of seconds until the
                token expires.
            **kwargs: Additional keyword arguments for creating the
                token.

        Returns:
            JsonWebToken: The newly created token instance.
        """
        expiration_seconds = expiration_seconds or DEFAULT_JWT_EXPIRY_SECONDS
        issued_at = now()
        expires_at = issued_at + timedelta(seconds=expiration_seconds)
        return super().create(
            issued_at=issued_at,
            expires_at=expires_at,
            **kwargs,
        )


class JsonWebToken(UUIDPrimaryKeyMixin):
    """
    Base model for managing JWT tokens with publication and expiration
    dates.
    """

    issued_at = models.DateTimeField(_('issued date and time'))
    expires_at = models.DateTimeField(_('expiry date and time'))

    objects = JsonWebTokenManager()

    class Meta:
        abstract = True

    @property
    def is_expired(self) -> bool:
        """Check if the token has expired.

        Returns:
            bool: True if the token has expired, False otherwise.
        """
        return self.expires_at < now()

    @property
    def payload(self) -> dict:
        """Return the token payload as a dictionary.

        Returns:
            dict: The token payload as a dictionary.
        """
        return {
            'exp': self.expires_at,
            'iat': self.issued_at,
            'jti': self.id.hex,
        }

    @property
    def jws(self) -> str:
        """Return the token as a JSON Web Signature (JWS).

        Returns:
            str: The token encoded as a JSON Web Signature (JWS).
        """
        return encode_token(self.payload)

    def revoke(self):
        """Revoke the token instance."""
        self.expires_at = now()
        self.save()
