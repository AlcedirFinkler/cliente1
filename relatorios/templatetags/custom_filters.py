from django import template

register = template.Library()

@register.filter
def get_month_name(value):
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    try:
        return months[int(value) - 1]
    except (ValueError, IndexError):
        return value

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter(name='get_item')
def get_item(dictionary, key):
    """
    Template filter to get an item from a dictionary using a key.
    Usage: {{ dictionary|get_item:key }}
    """
    if dictionary is None:
        return None
    return dictionary.get(key)