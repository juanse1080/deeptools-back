from django import template

from datetime import datetime
from datetime import timedelta
register = template.Library()

@register.filter
def date(date):
    data = datetime.strptime(str(date).split('.')[0], '%Y-%m-%d %H:%M:%S')
    now = datetime.now()
    resta = now - data
    print(now, data, resta)
    hours = int(resta.seconds/3600)
    minutes = int(resta.seconds/60)
    print(hours, minutes)
    if(resta.days == 0):
        if(hours <= 0):
            if(minutes <= 1):
                return "A minute ago"
            elif(minutes <= 30):
                return "%s minutes ago" % minutes
            return "A hour ago"
        elif(hours <= 10):
            return "%s hours ago" % hours
        return "Today at %s:%s" % (data.hour, data.minute)
    elif(resta.days <= 7):
        return "%s days ago" % resta.days
    return resta

@register.filter
def clean_date(date):
    data = datetime.strptime(str(date).split('.')[0], '%Y-%m-%d %H:%M:%S')
    return "%s/%s/%s" % (data.day, data.month, data.year)


@register.filter
def error(errors): #retorna el primer error del campo
    if errors:
        for i in errors:
            return i
    else:
        return ''       

@register.filter
def invalid(error, class_='is-invalid'): #verificacion del error
    return '' if not error else class_

@register.filter
def select(value='', real='-'): #selecciona el valor correspondiente
    return 'selected' if value == real else ''

@register.filter
def booleanSelect(value, real):
    return 'selected' if value is real else ''

@register.filter
def radio(value='', real='-'): #checkea el valor correspondiente
    return 'checked' if value == real else ''

@register.filter
def old(value): #checkea el valor correspondiente
    return value if value else ''

@register.filter
def substring(value, size): #retorna un string recortado con longitud igual a size
    return value[:size]+' ...' if len(value) > size else value+'.'

@register.filter
def max_list(array): #retorna el valor de count_comments
    return max(array)

@register.filter
def to_list(array, string_=False): #retorna el valor de count_comments
    list_ = "[" if not string_ else "['"
    for i in array:
        list_ += str(i)+", " if not string_ else str(i)+"', '"
    list_ = list_[:-2] + "]" if not string_ else list_[:-4] + "']"
    print(list_)
    return list_

@register.filter
def division(value, item):
    return 4

@register.filter
def get_item(vector, value):
    return vector[value]


