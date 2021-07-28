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



@register.filter
def duration(s):
    try:
        h = int(s / 3600)
    except:
        return s
    s %= 3600
    m = int(s / 60)
    s %= 60
    return f'{h}:{m:02d}:{s:02.1f}'
