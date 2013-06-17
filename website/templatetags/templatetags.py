from django import template
from django.contrib.humanize.templatetags.humanize import intcomma

register = template.Library()

def underscore(text):
    return text.replace(' ', '_')

register.filter('underscore', underscore)

def titlecase(text):
    return text.title()
    
register.filter('titlecase', titlecase)

def trunc(text):
    try:
        return int(text)
    except Exception:
        return text
    
register.filter('round', trunc)

def currency(text):
    try:
        dollars = round(float(text), 2)
        return "%s%s" % (intcomma(int(dollars)), ("%0.2f" % dollars)[-3:])
    except Exception:
        return text
        
register.filter('currency', currency)

def comma(text):
    '''Adds commas to large numbers.'''
    return intcomma(int(text))
    
register.filter('comma', comma)

def percent(text):
    try:
        return "%.02f" % (round(float(text) * 100, 2)) + '%'
    except Exception:
        return text
        
register.filter('percentage', percent)

def round2(text):
    try:
        return round(float(text), 2)
    except Exception:
        return text

register.filter('round', round2)