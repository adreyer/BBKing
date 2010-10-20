import StringIO

from django.template.loader import get_template
from django.conf import settings

from bbking import parser

DEFAULT_TAG_LIBRARIES = (
    'bbking.bbtags.text',
)

TAG_LIBRARIES = getattr(settings, "BBKING_TAG_LIBRARIES", DEFAULT_TAG_LIBRARIES)

class CompilationError(Exception):
    pass

class TagDoesNotExist(CompilationError):
    pass

class UnnamedTagException(CompilationError):
    pass

_TAGS = {}

def _load_tags():
    for lib in TAG_LIBRARIES:
        lib_module = __import__(lib, fromlist = ['__all__'])
        for cls_name in lib_module.__all__:
            tag = getattr(lib_module, cls_name)
            _TAGS[tag.tag_name] = tag

def get_tag(name):
    if not _TAGS:
        _load_tags()
    
    if name not in _TAGS:
        raise TagDoesNotExist, "%s is not a valid tag name" % name

    return _TAGS[name]

class BlockTag(object):
    def __init__(self, contents):
        self.contents = contents

    def render(self, context):
        output = StringIO.StringIO()
        for item in self.contents:
            output.write(item.render(context))
        return output.getvalue()

class LiteralTag(object):
    def __init__(self, value):
        self.value = value

    def render(self, context):
        return self.value

class BBTag(object):
    def __init__(self, contents):
        if not self.tag_name:
            raise UnnamedTagException

        self.contents = contents
        self.template = get_template("bbking/tags/%s.html" % self.tag_name)

    def update_context(self, context):
        pass

    def render(self, context):
        try:
            context.push()
            context['contents'] = self.contents.render(context)
            self.update_context(context)
            return self.template.render(context)
        finally:
            context.pop()

class BBTagWithArg(BBTag):
    def __init__(self, contents, arg):
        if not self.tag_name:
            raise UnnamedTagException

        self.contents = contents
        self.arg = arg
        self.template = get_template("bbking/tags/%s.html" % self.tag_name)

    def render(self, context):
        try:
            context.push()
            context['contents'] = self.contents.render(context)
            context['arg'] = self.arg
            self.update_context(context)
            return self.template.render(context)
        finally:
            context.pop()

class BBTagWithKWArgs(BBTag):
    def __init__(self, contents, **kwargs):
        if not self.tag_name:
            raise UnnamedTagException

        self.contents = contents
        self.kwargs = kwargs
        self.template = get_template("bbking/tags/%s.html" % self.tag_name)

    def render(self, context):
        try:
            context.push()
            context['contents'] = self.contents.render(context)
            for key,value in self.kwargs.items():
                context[key] = value
            self.update_context(context)
            return self.template.render(context)
        finally:
            context.pop()

def load_tags(contents):
    tags = []

    for item in contents:
        if isinstance(item, parser.Literal):
            tags.append(LiteralTag(item.value))
        else:
            tag = get_tag(item.name)
            children = load_tags(item.contents)
            if item.arg:
                tags.append(tag(children, item.arg))
            elif item.kwargs:
                tags.append(tag(children, **item.kwargs)) 
            else:
                tags.append(tag(children))

    if len(tags) == 1:
        return tags[0]

    return BlockTag(tags)
                
def compile(raw):
    parsed = parser.parser.parse(raw)
    if not parsed:
        raise CompilationError

    return load_tags(parsed)

