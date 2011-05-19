from django import template
from datetime import datetime


register = template.Library()


@register.filter(name='tuplesort')
def tuplesort(value, pos):
    r = sorted(value, key=lambda x: x[pos])
    return r

@register.filter(name='tuplesortreversed')
def tuplesortreversed(value, pos):
    r = sorted(value, key=lambda x: x[pos])
    r.reverse()
    return r

@register.filter(name='fromtimestamp')
def fromtimestamp(value):
    return datetime.utcfromtimestamp(value)
