from django import template
register = template.Library()

@register.filter
def dict_get(diccionario, clave):
    """
    Filtro para permitir acceder a un diccionario desde una plantilla.
    """
    if diccionario is None:
        return None
    return diccionario.get(clave)
