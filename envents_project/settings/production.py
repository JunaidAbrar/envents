"""
Production settings for envents_project project.

These settings are meant for production environments.
"""
import environ
from .base import *
from ..s3_storage import apply_s3_settings
from django.core.exceptions import ImproperlyConfigured
#Initialize environ
env = environ.Env()
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool('DEBUG', default=False)

# https://docs.djangoproject.com/en/dev/ref/settings/#allowed-hosts
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['enventsbd.com', 'envents-production.up.railway.app'])
CSRF_TRUSTED_ORIGINS = env.list('CSRF_TRUSTED_ORIGINS', default=['https://enventsbd.com', 'https://envents-production.up.railway.app'])

# Always disable Tailwind dev mode in production
TAILWIND_DEV_MODE = False

# Storage Configuration - Always use S3 in production
try:
    print("Configuring S3 storage for production...")
    apply_s3_settings(locals())
    print("✅ S3 storage configured for production")
except Exception as e:
    raise ImproperlyConfigured(f"S3 storage configuration failed in production: {e}")

# Remove WhiteNoise for static files in production since we're using S3
if 'whitenoise.middleware.WhiteNoiseMiddleware' in MIDDLEWARE:
    MIDDLEWARE.remove('whitenoise.middleware.WhiteNoiseMiddleware')

# Database
DATABASES = {
    'default': {
        'ENGINE': env('DB_ENGINE', default='django.db.backends.postgresql'),
        'NAME': env('DB_NAME'),         # no default
        'USER': env('DB_USER'),         # no default
        'PASSWORD': env('DB_PASSWORD'), # no default
        'HOST': env('DB_HOST'),         # no default (prevents falling back to "db")
        'PORT': env.int('DB_PORT', default=5432),
        'OPTIONS': env.json('DB_OPTIONS', default={"sslmode": "require"}),
    }
}



# Session configuration - use database-backed sessions
SESSION_ENGINE = 'django.contrib.sessions.backends.db'

# Email Configuration
EMAIL_BACKEND = env('EMAIL_BACKEND')
EMAIL_HOST = env('EMAIL_HOST')
EMAIL_PORT = env.int('EMAIL_PORT')
EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS')
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL')


# Security
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True

SESSION_COOKIE_SECURE = env.bool('SESSION_COOKIE_SECURE', default=True)
CSRF_COOKIE_SECURE = env.bool('CSRF_COOKIE_SECURE', default=True)
SECURE_HSTS_SECONDS = env.int('SECURE_HSTS_SECONDS', default=31536000)  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = env.bool('SECURE_HSTS_INCLUDE_SUBDOMAINS', default=True)
SECURE_HSTS_PRELOAD = env.bool('SECURE_HSTS_PRELOAD', default=True)
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'
