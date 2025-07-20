# finance/templatetags/finance_filters.py
from django import template

register = template.Library()

@register.filter
def intcomma(value):
    """Add commas to numbers (similar to humanize intcomma)"""
    try:
        return "{:,}".format(float(value))
    except (ValueError, TypeError):
        return value