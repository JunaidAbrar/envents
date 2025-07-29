#!/usr/bin/env python
"""
Debug storage configuration
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'envents_project.settings.development')
django.setup()

from django.conf import settings
from django.core.files.storage import default_storage

def debug_storage():
    print("=== Storage Configuration Debug ===")
    print(f"DEFAULT_FILE_STORAGE: {settings.DEFAULT_FILE_STORAGE}")
    print(f"MEDIA_ROOT: {settings.MEDIA_ROOT}")
    print(f"MEDIA_URL: {settings.MEDIA_URL}")
    print(f"default_storage: {default_storage}")
    print(f"default_storage class: {default_storage.__class__}")
    print(f"default_storage location: {getattr(default_storage, 'location', 'N/A')}")
    
    # Check if storages is in INSTALLED_APPS
    storages_apps = [app for app in settings.INSTALLED_APPS if 'storage' in app.lower()]
    print(f"Storage apps in INSTALLED_APPS: {storages_apps}")
    
    # Try to manually import MediaStorage
    try:
        from envents_project.storage_backends import MediaStorage
        print("✅ MediaStorage import successful")
        
        # Create instance
        ms = MediaStorage()
        print(f"MediaStorage instance: {ms}")
        print(f"MediaStorage bucket: {getattr(ms, 'bucket_name', 'N/A')}")
        
        # Test if we can instantiate it properly
        from django.core.files.storage import get_storage_class
        storage_class = get_storage_class(settings.DEFAULT_FILE_STORAGE)
        print(f"Storage class from settings: {storage_class}")
        
    except Exception as e:
        print(f"❌ MediaStorage error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_storage()
