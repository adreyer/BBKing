from django.template.loader import get_template

from bbking.parser import parser
from bbking.nodes import library

class LiteralNode(object):
    def __init__(self, value):
        self.value = value

    def render(self, context):
        return self.value

class BBNode(object):
    def __init__(self, name, content):
        self.name = name
        self.content = content
        self.template = get_template("bbcode/tags/%s.html" % name)

    def render(self, context):
        try:
            context.push()
            context['content'] = self.content.render(context)
            return template.render(context)
        finally:
            context.pop()

class CompilationError(object):
    pass

def compile(raw):
    parsed = parser.parse(raw)
    if not parsed:
        raise CompilationError

