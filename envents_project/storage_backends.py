import os
from storages.backends.s3boto3 import S3Boto3Storage


class StaticStorage(S3Boto3Storage):
    location = 'static'
    default_acl = None  # Don't set ACL when bucket has Block Public Access enabled
    bucket_acl = None   # Don't set bucket ACL
    object_acl = None   # Don't set object ACL
    querystring_auth = False  # Don't add authentication to URLs
    file_overwrite = True
    
    def _normalize_name(self, name):
        name = super()._normalize_name(name)
        return name
        
    def get_object_parameters(self, name):
        """
        Set proper MIME types for files based on extension
        """
        params = super().get_object_parameters(name)
        
        # Set content types for common static files
        content_types = {
            '.css': 'text/css',
            '.js': 'application/javascript',
            '.json': 'application/json',
            '.svg': 'image/svg+xml',
            '.woff': 'font/woff',
            '.woff2': 'font/woff2',
            '.ttf': 'font/ttf',
            '.eot': 'application/vnd.ms-fontobject',
        }
        
        # Find the file extension
        ext = os.path.splitext(name)[1].lower()
        
        # Set the content type if we have a mapping for this extension
        if ext in content_types:
            params['ContentType'] = content_types[ext]
            # Add cache headers for static assets
            params['CacheControl'] = 'max-age=31536000, immutable'
        
        return params


class MediaStorage(S3Boto3Storage):
    location = 'media'
    default_acl = None  # Don't set ACL when bucket has Block Public Access enabled
    bucket_acl = None   # Don't set bucket ACL
    object_acl = None   # Don't set object ACL
    querystring_auth = False  # Don't add authentication to URLs
    file_overwrite = False


def patch_default_storage():
    """
    Force Django to use the correct storage backend.
    This function patches the default_storage to ensure S3 is used.
    """
    from django.core.files import storage
    from django.conf import settings
    
    # Only patch if DEFAULT_FILE_STORAGE is set to our MediaStorage
    if settings.DEFAULT_FILE_STORAGE == 'envents_project.storage_backends.MediaStorage':
        # Create new MediaStorage instance
        media_storage = MediaStorage()
        
        # Replace the default storage
        storage.default_storage = media_storage
        
        print(f"✅ Patched default_storage to use: {media_storage}")
        return True
    
    return False
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print(f"MediaStorage initialized with location: {self.location}")
        print(f"MediaStorage bucket: {self.bucket_name}")
        
        # Check for potential MEDIA_ROOT conflicts
        from django.conf import settings
        media_root = getattr(settings, 'MEDIA_ROOT', None)
        if media_root:
            print(f"WARNING: MEDIA_ROOT is set to {media_root} but using S3 storage!")
        else:
            print("MEDIA_ROOT is properly cleared for S3 storage")
    
    def _save(self, name, content):
        """
        Override _save to add debugging and ensure proper saving
        """
        print(f"MediaStorage._save called with name: {name}")
        print(f"Content type: {type(content)}, size: {getattr(content, 'size', 'unknown')}")
        try:
            result = super()._save(name, content)
            print(f"MediaStorage._save successful, result: {result}")
            return result
        except Exception as e:
            print(f"MediaStorage._save failed with error: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def get_available_name(self, name, max_length=None):
        """
        Override to add debugging
        """
        result = super().get_available_name(name, max_length)
        print(f"MediaStorage.get_available_name: {name} -> {result}")
        return result


def patch_default_storage():
    """
    Patch Django's default storage to ensure S3 is used
    """
    from django.core.files.storage import default_storage
    from django.conf import settings
    
    # Only patch if we're using S3
    if hasattr(settings, 'DEFAULT_FILE_STORAGE') and 'MediaStorage' in settings.DEFAULT_FILE_STORAGE:
        print("Patching default storage to use S3")
        # Force the default storage to be our MediaStorage
        default_storage._wrapped = MediaStorage()
    else:
        print("Not patching storage - not using S3")
