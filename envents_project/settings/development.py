"""
Development settings for envents_project project.

These settings are meant for local development environments.
For now, we import from the original settings.py file to ensure compatibility.
"""

import sys
import os
from pathlib import Path

# Import all settings from the original settings.py file
from .base import *
# Import original settings for compatibility during transition
import sys
import importlib.util
spec = importlib.util.spec_from_file_location(
    "original_settings", 
    str(Path(__file__).resolve().parent.parent / "settings.py")
)
original_settings = importlib.util.module_from_spec(spec)
spec.loader.exec_module(original_settings)

# Override with development-specific settings
DEBUG = True
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

# MCP (Model Context Protocol) Configuration
MCP_CONFIG = {
    "mcpServers": {
        "postgres": {
            "command": "npx",
            "args": [
                "-y",
                "@modelcontextprotocol/server-postgres",
                env('MCP_DATABASE_URL', default="postgresql://postgres:password@localhost:5432/envents")
            ]
        }
    }
}
