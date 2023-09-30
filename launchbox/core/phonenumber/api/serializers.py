from rest_framework.serializers import CharField

from ..validators import PhoneNumberValidator


class PhoneNumberField(CharField):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        validator = PhoneNumberValidator()
        self.validators.append(validator)
