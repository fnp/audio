import django.template


register = django.template.Library()


@register.simple_tag
def last_name(author):
    # TODO: we should reference the Catalogue to get proper last name.
    if author.lower() == 'autor nieznany':
        return
    parts = author.split(' ')
    for part in reversed(parts):
        if part.startswith('('): continue
        return part
