from django.conf import settings

JWT_SECRET_KEY = getattr(settings, 'JWT_SECRET_KEY', settings.SECRET_KEY)
