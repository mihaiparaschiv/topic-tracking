from django import template


register = template.Library()


@register.filter(name='mongoid')
def mongoid(model):
    value = model._id
    return unicode(value)
