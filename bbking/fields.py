import hashlib

from django.core.cache import cache
from django.db.models import signals

import bbking

def BBKingField(object):
    def __init__(self, text_field='body', hash_field=None):
        self.text_field = text_field
        self.hash_field = hash_field

    def contribute_to_class(self, cls, name):
        self.name = name
        self.model = cls

        if self.hash_field:
            signals.pre_save.connect(self.update_hash_field, sender=cls)

        setattr(cls, name, self)

    def __get__(self, obj):
        raw = getattr(obj, self.text_field)

        if self.hash_field:
            hash_key = getattr(obj, self.hash_field)
            if hash_key:
                compiled = cache.get('bbking:%s' % hash_key)
            else:
                compiled = bbking.LiteralValue(raw)
        else:
            hash_key = None

        if not compiled:
            try:
                compiled = bbking.compile(raw)
            except CompilationError:
                compiled = bbking.LiteralValue(raw)

            if hash_key:
                cache.set('bbking:%s' % hash_key, compiled)

        return compiled

    def update_hash_field(self, signal, sender, args, kwargs):
        raw = getattr(sender, self.text_field)

        hash_key = hashlib.sha1(raw).hexdigest()
        setattr(sender, self.hash_field, hash_key)

