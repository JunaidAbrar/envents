"""
Context processors for the Envents project
"""
from django.conf import settings

def debug(request):
    """Add debug flag to context for all templates"""
    return {'debug': settings.DEBUG}
