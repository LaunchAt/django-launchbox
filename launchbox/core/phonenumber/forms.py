from django.forms.fields import CharField
from django.forms.widgets import Input

from . import validators


class PhoneNumberInput(Input):
    input_type = 'tel'
    template_name = 'django/forms/widgets/input.html'


class PhoneNumberField(CharField):
    widget = PhoneNumberInput
    default_validators = [validators.PhoneNumberValidator()]

    def __init__(self, **kwargs):
        kwargs.setdefault('max_length', 32)
        super().__init__(strip=True, **kwargs)
