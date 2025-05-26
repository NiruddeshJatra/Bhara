# config/settings/development.py
from .base import *

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'noreply@bhara.xyz'
EMAIL_FROM = 'noreply@bhara.xyz'  # Required by the verification email task
EMAIL_BCC = ''

# CORS settings
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# URL settings for email verification
BACKEND_URL = 'http://localhost:8000'
FRONTEND_URL = 'http://localhost:3000'