from django import template

register = template.Library()

@register.filter()
def dict_key(d, k):
    '''Returns the given key from a dictionary.'''
    return d[k]

@register.filter()
def list_key(l, k):
    '''[(x, y), (a, b)]] | list_key:"x" returns y'''
    for item in l:
        if item[0] == k:
            return item[1]