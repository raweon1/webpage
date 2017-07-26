from django import template

register = template.Library()


@register.filter(name="zip")
def zip_test(a, b):
    return zip(a, b)
