import phonenumbers
from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _

from .utils import parse_phone_number


@deconstructible
class PhoneNumberValidator:
    message = _("`%(value)s` value has an invalid international phone number format.")
    code = 'invalid_phone_number'

    def __init__(self, message=None, code=None):
        if message is not None:
            self.message = message
        if code is not None:
            self.code = code

    def __call__(self, value):
        try:
            parsed_number = parse_phone_number(value)
        except phonenumbers.NumberParseException:
            raise ValidationError(self.message, code=self.code, params={'value': value})
        if not phonenumbers.is_valid_number(parsed_number):
            raise ValidationError(self.message, code=self.code, params={'value': value})

    def __eq__(self, other):
        return (
            isinstance(other, PhoneNumberValidator)
            and self.message == other.message
            and self.code == other.code
        )


validate_phone_number = PhoneNumberValidator()
