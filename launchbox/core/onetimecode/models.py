from datetime import timedelta

from django.db import models
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _

from ..models import UUIDPrimaryKeyMixin
from .settings import DEFAULT_OTP_EXPIRY_SECONDS
from .utils import generate_otp, uuid_to_base32_code


class OneTimeCodeQuerySet(models.QuerySet):
    def expired_set(self) -> models.QuerySet:
        """Return a queryset containing expired code instances.

        Returns:
            QuerySet: A queryset containing expired code instances.
        """
        return self.filter(expires_at__lte=now())

    def clean_up(self) -> tuple[int, dict[str, int]]:
        """Delete expired code instances from the database.

        Returns:
            tuple: A tuple containing the number of deleted codes and a
                dictionary with information about the deletion
                operation.
        """
        return self.expired_set().delete()


class OneTimeCodeManager(
    models.Manager.from_queryset(OneTimeCodeQuerySet),  # type: ignore
):
    def generate(
        self,
        *,
        expiration_seconds: int | None = None,
        **kwargs,
    ) -> 'OneTimeCode':
        """
        Create a new code instance with automatic assignment of
        `issued_at` and `expires_at` fields based on the provided
        `expiration_seconds`.

        Args:
            expiration_seconds (int | None): The duration in seconds until
                the new code expires.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            OneTimeCode: The created code instance.
        """
        expiration_seconds = expiration_seconds or DEFAULT_OTP_EXPIRY_SECONDS
        issued_at = now()
        expires_at = issued_at + timedelta(seconds=expiration_seconds)
        return super().create(
            issued_at=issued_at,
            expires_at=expires_at,
            **kwargs,
        )

    def refresh_or_generate(
        self,
        *,
        expiration_seconds: int | None = None,
        **kwargs,
    ) -> 'OneTimeCode':
        """
        Attempt to find a code instance matching the provided conditions
        (kwargs). If found, refresh the code with a new expiration time.
        If not found, generate a new code instance.

        Args:
            expiration_seconds (int | None): The duration in seconds until
                the new code expires.
            **kwargs: Arbitrary keyword arguments that will be used to
                filter the existing code instances.

        Returns:
            OneTimeCode: The refreshed or created code instance.
        """
        expiration_seconds = expiration_seconds or DEFAULT_OTP_EXPIRY_SECONDS
        try:
            code: OneTimeCode = self.filter(**kwargs).get()
        except OneTimeCode.DoesNotExist:
            code = self.generate(expiration_seconds=expiration_seconds, **kwargs)
        else:
            code.refresh(expiration_seconds=expiration_seconds)
        return code


class OneTimeCode(UUIDPrimaryKeyMixin):
    issued_at = models.DateTimeField(_('issued date and time'))
    expires_at = models.DateTimeField(_('expiry date and time'))

    objects = OneTimeCodeManager()

    class Meta:
        abstract = True

    @property
    def is_expired(self) -> bool:
        """Check if the code has expired.

        Returns:
            bool: True if the code has expired, False otherwise.
        """
        return self.expires_at < now()

    @property
    def code(self) -> str:
        """Get the Base32 encoded string of the original ID as a code.

        Returns:
            str: The Base32 encoded string of the original ID as a code.
        """
        return uuid_to_base32_code(self.id)

    @property
    def otp(self) -> str:
        """Generate a six-digit code as a One Time Password (OTP).

        Returns:
            str: The six-digit code as a One Time Password (OTP).
        """
        return generate_otp(self.code, self.issued_at)

    def validate_code(self, code: str) -> bool:
        """Validate the given code.

        Args:
            code (str): The code to be validated.

        Returns:
            bool: True if the provided code matches the generated code
                and it is not expired, False otherwise.
        """
        return not self.is_expired and self.code == code

    def validate_otp(self, otp: str) -> bool:
        """Validate the given six-digit One Time Password (OTP).

        Args:
            six_digits_code (str): The six-digit code to be validated.

        Returns:
            bool: True if the provided code matches the generated
                six-digit code and it is not expired, False otherwise.
        """
        return not self.is_expired and self.otp == otp

    def refresh(self, *, expiration_seconds: int | None = None) -> None:
        """Refresh the code with a new publication and expiration time.

        Args:
            expiration_seconds (int | None): The duration in seconds until
                the new code expires.
        """
        expiration_seconds = expiration_seconds or DEFAULT_OTP_EXPIRY_SECONDS
        self.issued_at = now()
        self.expires_at = self.issued_at + timedelta(seconds=expiration_seconds)
        self.save(update_fields=['issued_at', 'expires_at'])
