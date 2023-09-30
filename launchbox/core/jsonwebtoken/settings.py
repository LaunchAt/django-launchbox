from django.conf import settings

DEFAULT_JWT_EXPIRY_SECONDS = getattr(settings, 'DEFAULT_JWT_EXPIRY_SECONDS', 3600)

JWT_SECRET_KEY = getattr(settings, 'JWT_SECRET_KEY', settings.SECRET_KEY)
