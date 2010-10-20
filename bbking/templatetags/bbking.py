from django import template

import bbking

register = template.Library()

class BBCodeNode(template.Node):
    def __init__(self, varname):
        self.varname = template.Variable(content)

    def render(self, context):
        try:
            raw = self.content.resolve(context)
        except template.VariableDoesNotExist:
            return ''

        compiled = bbking.compile(raw)
        
        if not compiled:
            return raw
        else:
            return compiled.render(context)

@register.tag
def bbcode(parser, token):
    try:
        tagname, var = token.contents.split()
    except ValueError:
        raise template.TemplateSyntaxError, "bbcode tag requires one argument"
    return BBCodeNode(var)
