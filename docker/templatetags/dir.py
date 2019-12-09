from django import template
register = template.Library()

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


