from django.conf import settings

DEFAULT_OTP_EXPIRY_SECONDS = getattr(settings, 'DEFAULT_OTP_EXPIRY_SECONDS', 600)
