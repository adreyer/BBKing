import re

from bbking import BBTag

__all__ = ['BBTagURL', 'BBTagImg', 'BBTagYouTube']

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

class BBTagYouTube(BBTag):
    tag_name = 'youtube'

    _video_re = re.compile(r"v=(\w+)")
    _base_url = 'http://www.youtube.com/v/%s&amp;hl=en&amp;fs=1&amp;'

    def update_context(self, context):
        url = context['contents']

        match = self._video_re.search(url)
        if not match:
            context['valid_url'] = False
            return

        context['valid_url'] = True
        context['url'] = self._base_url % match.group(1)

    @classmethod
    def usage(cls):
        return [
            '[youtube]http://example.com/blam.gif[/youtube]',
        ]

