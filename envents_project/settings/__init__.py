"""
Settings initialization.

This file determines which settings to load based on the DJANGO_SETTINGS_MODULE environment variable.
By default, it will load the development settings.
"""

import os
import sys
from pathlib import Path

# Set DJANGO_SETTINGS_MODULE to production by default
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'envents_project.settings.production')

# This file is intentionally left empty
# Settings are loaded directly from development.py or production.py 
# based on the DJANGO_SETTINGS_MODULE environment variable