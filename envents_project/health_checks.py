"""
Health checks for the Envents application.
This module provides endpoints for monitoring the application's health.
"""

from django.http import JsonResponse
from django.views.decorators.http import require_GET
import psycopg2
from django.conf import settings
import boto3
import redis
import json
import logging

logger = logging.getLogger(__name__)

@require_GET
def health_check(request):
    """
    Basic health check endpoint that confirms the application is running.
    Returns a 200 OK response with a simple status message.
    """
    return JsonResponse({"status": "ok", "message": "Envents application is running"})

@require_GET
def full_health_check(request):
    """
    Full health check that tests all critical components including:
    - Database connection
    - S3 storage
    - Redis (if used)
    """
    status = {
        "status": "ok",
        "database": check_database(),
        "s3_storage": check_s3_storage(),
        "redis": check_redis()
    }
    
    # If any component is not ok, set overall status to error
    if "error" in status["database"] or "error" in status["s3_storage"] or "error" in status["redis"]:
        status["status"] = "error"
        return JsonResponse(status, status=500)
    
    return JsonResponse(status)

def check_database():
    """Check database connection"""
    try:
        # Attempt to connect to the database
        conn = psycopg2.connect(
            dbname=settings.DATABASES['default']['NAME'],
            user=settings.DATABASES['default']['USER'],
            password=settings.DATABASES['default']['PASSWORD'],
            host=settings.DATABASES['default']['HOST'],
            port=settings.DATABASES['default']['PORT'],
        )
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
        conn.close()
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        return {"status": "error", "message": str(e)}

def check_s3_storage():
    """Check S3 storage connection"""
    try:
        s3 = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME,
        )
        # Check if bucket exists
        s3.head_bucket(Bucket=settings.AWS_STORAGE_BUCKET_NAME)
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"S3 storage health check failed: {str(e)}")
        return {"status": "error", "message": str(e)}

def check_redis():
    """Check Redis connection"""
    try:
        # Extract host and port from REDIS_URL
        redis_url = getattr(settings, 'REDIS_URL', 'redis://redis:6379/1')
        # Parse the URL
        host = 'redis'
        port = 6379
        
        if '://' in redis_url:
            parts = redis_url.split('://')[-1].split(':')
            if len(parts) > 1:
                host = parts[0]
                port = int(parts[1].split('/')[0])
        
        # Connect to Redis
        r = redis.Redis(host=host, port=port)
        r.ping()
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Redis health check failed: {str(e)}")
        return {"status": "error", "message": str(e)}