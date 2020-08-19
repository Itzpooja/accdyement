from django import template
from dyeing.models import *
register = template.Library()

@register.filter
def multiply(value, arg):
    a = value*arg
    ans = "{:.2f}".format(a)
    return ans