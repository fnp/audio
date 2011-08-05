from django import template

register = template.Library()

@register.inclusion_tag('archive/tags/multiple_tags_table.html')
def multiple_tags_table(tags, table=True):
    return locals()


@register.inclusion_tag('archive/tags/tags_table.html')
def tags_table(tags, table=True):
    return locals()
