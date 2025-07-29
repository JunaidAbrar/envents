"""
Unified S3 storage configuration for both development and production.

This module provides a consistent S3 storage setup that eliminates
the complexity of having different storage backends for different environments.
"""

import os
import environ
from django.core.exceptions import ImproperlyConfigured

# Initialize environ
env = environ.Env()

def configure_s3_storage():
    """
    Configure S3 storage settings.
    Returns a dictionary of S3-related settings.
    """
    try:
        # Required S3 credentials
        aws_access_key_id = env('AWS_ACCESS_KEY_ID')
        aws_secret_access_key = env('AWS_SECRET_ACCESS_KEY')
        aws_storage_bucket_name = env('AWS_STORAGE_BUCKET_NAME')
        
        # Optional S3 settings with defaults
        aws_s3_region_name = env('AWS_S3_REGION_NAME', default='ap-south-1')
        aws_s3_custom_domain = env(
            'AWS_S3_CUSTOM_DOMAIN', 
            default=f'{aws_storage_bucket_name}.s3.{aws_s3_region_name}.amazonaws.com'
        )
        
        s3_settings = {
            # Required credentials
            'AWS_ACCESS_KEY_ID': aws_access_key_id,
            'AWS_SECRET_ACCESS_KEY': aws_secret_access_key,
            'AWS_STORAGE_BUCKET_NAME': aws_storage_bucket_name,
            
            # S3 configuration
            'AWS_S3_REGION_NAME': aws_s3_region_name,
            'AWS_S3_CUSTOM_DOMAIN': aws_s3_custom_domain,
            'AWS_DEFAULT_ACL': None,  # Don't set ACL when bucket has Block Public Access
            'AWS_S3_FILE_OVERWRITE': False,
            'AWS_QUERYSTRING_AUTH': False,
            'AWS_S3_SIGNATURE_VERSION': 's3v4',
            'AWS_S3_ADDRESSING_STYLE': 'virtual',
            'AWS_S3_URL_PROTOCOL': 'https:',
            
            # Storage backends
            'STATICFILES_STORAGE': 'envents_project.storage_backends.StaticStorage',
            'DEFAULT_FILE_STORAGE': 'envents_project.storage_backends.MediaStorage',
            
            # URLs
            'STATIC_URL': f'https://{aws_s3_custom_domain}/static/',
            'MEDIA_URL': f'https://{aws_s3_custom_domain}/media/',
            
            # Clear local storage settings
            'MEDIA_ROOT': None,
            
            # Ensure storages app is included
            'INSTALL_STORAGES': True,
        }
        
        return s3_settings
        
    except environ.ImproperlyConfigured as e:
        raise ImproperlyConfigured(f"S3 configuration error: {e}")

def apply_s3_settings(settings_dict):
    """
    Apply S3 settings to a Django settings dictionary.
    
    Args:
        settings_dict: The Django settings dictionary to update
    """
    s3_settings = configure_s3_storage()
    
    # Apply all S3 settings
    settings_dict.update(s3_settings)
    
    # Add storages to INSTALLED_APPS if needed
    if s3_settings.get('INSTALL_STORAGES') and 'storages' not in settings_dict.get('INSTALLED_APPS', []):
        settings_dict.setdefault('INSTALLED_APPS', []).append('storages')
    
    # Apply the storage patch
    try:
        from envents_project.storage_backends import patch_default_storage
        patch_default_storage()
        print("✅ S3 storage configured and patched successfully")
    except ImportError:
        print("⚠️  Storage patch not applied (storage_backends not available)")
    
    return True

def get_fallback_settings():
    """
    Get fallback local storage settings when S3 is not available.
    """
    return {
        'DEFAULT_FILE_STORAGE': 'django.core.files.storage.FileSystemStorage',
        'STATICFILES_STORAGE': 'django.contrib.staticfiles.storage.StaticFilesStorage',
        'MEDIA_URL': '/media/',
        'STATIC_URL': '/static/',
        # MEDIA_ROOT should be set in base settings
    }
