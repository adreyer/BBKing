
from bbking import BBTag

__all__ = ['BBTagURL', 'BBTagImg']

class BBTagURL(BBTag):
    tag_name = 'url'

    def __init__(self, contents, arg=None):
        super(BBTagURL, self).__init__(contents)
        self.arg = arg

    def update_context(self, context):
        if self.arg:
            context['url'] = self.arg.render(context)
        else:
            context['url'] = context['contents']

    @classmethod
    def usage(cls):
        return [
            '[url=http://example.com/]Example link text[/url]',
            '[url]http://example.com/[/url]',
        ]

class BBTagImg(BBTag):
    tag_name = 'img'

    @classmethod
    def usage(cls):
        return [
            '[img]http://example.com/blam.gif[/img]',
        ]
