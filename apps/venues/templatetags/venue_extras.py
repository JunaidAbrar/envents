from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.simple_tag(takes_context=True)
def param_replace(context, **kwargs):
    """
    Return encoded URL parameters that are the same as the current
    request's parameters, only with the specified GET parameters modified.
    """
    params = context['request'].GET.copy()
    for key, value in kwargs.items():
        params[key] = value
    return params.urlencode()

@register.filter
def split(value, arg):
    """
    Split a string on a delimiter.
    """
    return value.split(arg)