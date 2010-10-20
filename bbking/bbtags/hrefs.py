
from bbking import BBTag

__all__ = ['BBTagURL', 'BBTagImg']

class BBTagURL(BBTag):
    tag_name = 'url'

    def __init__(self, contents, arg=None):
        super(BBTagURL, self).__init__(contents)
        self.arg = arg

    def update_context(self, context):
        if self.arg:
            context['url'] = self.arg
        else:
            context['url'] = context['contents']

class BBTagImg(BBTag):
    tag_name = 'img'
