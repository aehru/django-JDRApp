from django import template
register = template.Library()

@register.filter
def get_item(lst, key):
    if key in lst:
        return lst[key]
    else:
        return None