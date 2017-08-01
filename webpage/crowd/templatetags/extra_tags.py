from django import template

register = template.Library()


@register.filter(name="zip")
def zip_test(a, b):
    return zip(a, b)


@register.inclusion_tag("crowd/stimulus_tag.html")
def display_stimulus(stimulus):
    return {"stimulus": stimulus}