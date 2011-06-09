from django import template

register = template.Library()

@register.simple_tag
def multiple_tags_table(tags):
    return template.loader.render_to_string(
            "archive/tags/multiple_tags_table.html",
            {"tags": tags}
        )


#@register.simple_tag
#def multiple_tags_table(tags):
#    return template.loader.render_to_string(
#            "archive/tags/multiple_tags_table.html",
#            {"tags": tags}
#        )

