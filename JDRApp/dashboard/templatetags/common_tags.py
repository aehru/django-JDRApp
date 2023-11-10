from django import template

register = template.Library()

@register.filter()
def dict_key(d, k):
    '''Returns the given key from a dictionary.'''
    return d[k]