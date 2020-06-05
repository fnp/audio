from django import template

register = template.Library()


@register.inclusion_tag('archive/tags/multiple_tags_table.html')
def multiple_tags_table(tags, table=True):
    new_tags = {}
    if tags:
        for k, v in tags.items():
            if isinstance(v, list):
                new_tags[k] = v
            else:
                new_tags[k] = [v]
    return {"tags": new_tags, "table": table}


@register.inclusion_tag('archive/tags/tags_table.html')
def tags_table(tags, table=True):
    if tags is None:
        tags = {}
    return locals()


@register.inclusion_tag("archive/status.html")
def status(audiobook, format):
    if format == "youtube" and audiobook.youtube_id:
        link = f"https://youtu.be/{audiobook.youtube_id}"
    else:
        link = None
    return {
        "published": getattr(audiobook, f"{format}_published"),
        "status": getattr(audiobook, f"get_{format}_status_display")(),
        "format": format,
        "link": link,
    }
