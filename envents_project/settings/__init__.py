"""
Settings initialization.

This file determines which settings to load based on the DJANGO_SETTINGS_MODULE environment variable.
By default, it will load the development settings.
"""

import os
import sys
from pathlib import Path

# Point to the original settings during transition
# This makes sure the application works while we're setting up the new structure
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from envents_project.settings import *