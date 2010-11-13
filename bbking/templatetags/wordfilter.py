import re
from django import template
from ..models import WordFilter

register = template.Library()

@register.filter
def wordfilter(value):
    
    regexes = []
    #try to cache regexes and recover them
    if True:
        filters = WordFilter.objects.filter(
                    active=True).order_by('-priority')
        regexes = []
        for filter in filters:
            if filter.ignore_case:
                regex = re.compile(filter.base_re, re.IGNORECASE)
            else: 
                regex = re.compile(filter.base_re)
            regexes.append((regex,filter.base_replace))


    for regex, rep in regexes:
        value = regex.sub(rep,value)
    return value
