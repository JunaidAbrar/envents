"""
Development settings for envents_project project.

These settings are meant for local development environments.
"""

import os
from pathlib import Path

# Import all settings from the base.py file
from .base import *

# Import unified S3 storage configuration
from ..s3_storage import apply_s3_settings, get_fallback_settings
import environ

env = environ.Env()

# Force S3 usage in development for consistency with production
USE_S3_IN_DEV = env.bool('USE_S3_IN_DEV', default=True)

# Override with development-specific settings
DEBUG = True
TAILWIND_DEV_MODE = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY', default='django-insecure-(5cf@mecypkt#jrf=^2n^3&u+qth4=!#5ryxw%pw7%=liv-b-+')

# Database
DATABASES = {
    'default': {
        'ENGINE': env('DB_ENGINE', default='django.db.backends.postgresql'),
        'NAME': env('DB_NAME', default='envents'),
        'USER': env('DB_USER', default='postgres'),
        'PASSWORD': env('DB_PASSWORD', default='password'),
        'HOST': env('DB_HOST', default='localhost'),
        'PORT': env('DB_PORT', default='5432'),
    }
}

# Email Configuration
EMAIL_BACKEND = env('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = env('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = env.int('EMAIL_PORT', default=587)
EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS', default=True)
EMAIL_HOST_USER = env('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', default='webmaster@localhost')

# Storage Configuration - Use S3 by default for consistency
if USE_S3_IN_DEV:
    try:
        print("Configuring S3 storage for development...")
        # Use unified S3 configuration
        apply_s3_settings(locals())
        print("✅ S3 storage enabled in development")
        
    except Exception as e:
        print(f"❌ S3 configuration failed: {e}")
        print("🔄 Falling back to local storage")
        # Apply fallback settings
        fallback_settings = get_fallback_settings()
        locals().update(fallback_settings)
        USE_S3_IN_DEV = False
else:
    print("📁 Using local storage in development")
    fallback_settings = get_fallback_settings()
    locals().update(fallback_settings)
