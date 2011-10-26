from django import template

register = template.Library()

@register.inclusion_tag('archive/tags/multiple_tags_table.html')
def multiple_tags_table(tags, table=True):
    new_tags = {}
    for k, v in tags.items():
        if isinstance(v, list):
            new_tags[k] = v
        else:
            new_tags[k] = [v]
    return {"tags": new_tags, "table": table}


@register.inclusion_tag('archive/tags/tags_table.html')
def tags_table(tags, table=True):
    return locals()
