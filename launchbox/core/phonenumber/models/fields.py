import phonenumbers
from django.core.exceptions import ValidationError
from django.db.models import CharField
from django.db.models.query_utils import DeferredAttribute
from django.utils.translation import gettext_lazy as _

from .. import forms
from ..utils import format_phone_number, parse_phone_number
from ..validators import validate_phone_number


class PhoneNumberDescriptor(DeferredAttribute):
    def __get__(self, instance, owner):
        if instance is None:
            return self
        raw_value = instance.__dict__[self.field.attname]
        return parse_phone_number(raw_value)

    def __set__(self, instance, value):
        instance.__dict__[self.field.attname] = self.field.get_prep_value(value)


class PhoneNumberField(CharField):
    default_validators = [validate_phone_number]
    description = _('Phone number')
    default_error_messages = {'invalid': validate_phone_number.message}
    descriptor_class = PhoneNumberDescriptor

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('max_length', 32)
        super().__init__(*args, **kwargs)

    def parse_number(self, value):
        parse_value = value if isinstance(value, str) else ''
        try:
            return parse_phone_number(parse_value)
        except phonenumbers.NumberParseException:
            raise ValidationError(
                self.error_messages['invalid'],
                code='invalid_phone_number',
                params={'value': value},
            )

    def to_python(self, value):
        if value is None:
            return value
        return self.parse_number(value)

    def get_prep_value(self, value):
        value = super().get_prep_value(value)
        if value is None:
            return value
        if not isinstance(value, phonenumbers.PhoneNumber):
            value = self.parse_number(value)
        return format_phone_number(value)

    def formfield(self, **kwargs):
        return super().formfield(**{'form_class': forms.PhoneNumberField, **kwargs})
