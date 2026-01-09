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

# Database - Railway + Neon (DATABASE_URL required)
# Fail fast if DATABASE_URL is missing
if not env.str('DATABASE_URL', default=''):
    raise ImproperlyConfigured(
        "DATABASE_URL is required in production. "
        "Please set DATABASE_URL environment variable with your Neon connection string. "
        "Example: postgresql://user:password@host:5432/dbname?sslmode=require"
    )

DATABASES = {
    "default": env.db("DATABASE_URL")
}

# Ensure SSL is enforced for Neon Postgres
# (DATABASE_URL should already include sslmode=require, but ensure it's set)
if 'OPTIONS' not in DATABASES['default']:
    DATABASES['default']['OPTIONS'] = {}
if 'sslmode' not in DATABASES['default']['OPTIONS']:
    DATABASES['default']['OPTIONS']['sslmode'] = 'require'

# Connection pooling - critical for performance with remote Neon database
# Keeps connections alive for 10 minutes, drastically reducing connection overhead
DATABASES['default']['CONN_MAX_AGE'] = 600  # 10 minutes
DATABASES['default']['CONN_HEALTH_CHECKS'] = True  # Verify connection health before reuse




# Session configuration - use database-backed sessions
SESSION_ENGINE = 'django.contrib.sessions.backends.db'

# Cache Configuration - Using local memory cache (no Redis required)
# Fast in-memory caching for single-server deployments
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'envents-cache',
        'OPTIONS': {
            'MAX_ENTRIES': 10000,
        }
    }
}

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
SECURE_SSL_REDIRECT = env.bool('SECURE_SSL_REDIRECT', default=True)

SESSION_COOKIE_SECURE = env.bool('SESSION_COOKIE_SECURE', default=True)
CSRF_COOKIE_SECURE = env.bool('CSRF_COOKIE_SECURE', default=True)

# SECURE_HSTS_SECONDS - Robust handling for Railway
# Allow env values like "False", "0", "off", "no" without crashing
_raw_hsts = env.str('SECURE_HSTS_SECONDS', default='31536000').strip()
SECURE_HSTS_SECONDS = 0 if _raw_hsts.lower() in ('false', '0', 'off', 'no') else int(_raw_hsts)

SECURE_HSTS_INCLUDE_SUBDOMAINS = env.bool('SECURE_HSTS_INCLUDE_SUBDOMAINS', default=True)
SECURE_HSTS_PRELOAD = env.bool('SECURE_HSTS_PRELOAD', default=True)
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'
