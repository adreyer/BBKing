
from bbking import BBTag

__all__ = ['BBQuote']

class BBQuote(BBTag):
    takes_arg = True
    tag_name = 'quote'

    def __init__(self, contents, arg=None):
        super(BBQuote, self).__init__(contents)
        self.arg = arg

    def update_context(self, context):
        if self.arg:
            context['cite'] = self.arg

