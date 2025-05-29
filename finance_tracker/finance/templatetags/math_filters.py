from django import template

register = template.Library()

@register.filter
def dash_offset(value):
    try:
        value = float(value)
    except (ValueError, TypeError):
        value = 0
    # Calculate stroke-dashoffset as per your circle logic
    # Assuming max offset is 282 (circumference)
    offset = 282 - (value * 2.82)  # 2.82 = 282/100 for percentage scale
    return offset