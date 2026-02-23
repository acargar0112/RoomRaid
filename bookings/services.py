from django.db.models import Q, F, Count
from .models import Booking, Space
from django.contrib.auth import get_user_model
User = get_user_model()

# 1) Q OBJECTS

def buscar_reservas(cliente=None, espacio=None, estado=None, fecha_inicio=None, fecha_fin=None):
    """
    Permite hacer búsquedas avanzadas por cliente, espacio, estado y rango de fechas.
    Todos los parametros son opciones, para que no haya problemas si solo se quiere buscar por alguno en concreto.
    RETURN: Devuelve un queryset filtado usando Q objects.
    La variable "qs" significa "QuerySet"
    """

    qs= Booking.objects.all()

    if cliente:
        qs = qs.filter(Q(cliente=cliente))
    if espacio:
        qs = qs.filter(Q(espacio=espacio))
    if estado:
        qs = qs.filter(Q(estado=estado))
    if fecha_inicio and fecha_fin:
        qs = qs.filter(Q(fecha__range=(fecha_inicio, fecha_fin)))

    return qs


def filtrar_espacios(capacidad_minima=None, recurso=None):
    """
    Devuelve espacios filtrados por:
    - Capacidad mínima
    - Activos
    """

    qs = Space.objects.filter(activo=True)

    if capacidad_minima and recurso:
        qs = qs.filter(Q(capacidad__gte=capacidad_minima) | Q(recursos=recurso))
    elif capacidad_minima:
        qs = qs.filter(capacidad__gte=capacidad_minima)
    elif recurso:
        qs = qs.filter(recursos=recurso)

    return qs


# 2) F EXPRESSIONS

def incrementar_contador_reservas(espacio):
    """
    Incrementa el contador de reservas de un espacio usando F expressions.
    Se quedará comentada hasta poder añadir el campo "contador_reservas" al modelo (Ya que hay un PR y si lo cambio ahora podría dar problemas)
    """
    espacio.contador_reservas = F("contador_reservas") + 1
    espacio.save(update_fields=["contador_reservas"])


# 3) ANNOTATE

def espacios_con_numero_de_franjas():
    """
    Devuelve los espacios con el número total de franjas reservadas.
    """

    return Space.objects.annotate(total_franjas=Count("reservas__franjas", distinct=True)).order_by("-total_franjas")


def clientes_con_reservas_activas():
    """
    Devuelve clientes con el número de reservas activas
    """

    return User.objects.annotate(reservas_activas=Count("reservas", filter=Q(reservas__estado="confirmada"))).order_by("-reservas_activas")

def top_salas_mas_usadas(top=5):
    """
    Muestra las salas mas usadas.
    Máximo 5.
    """
    return Space.objects.annotate(total_reservas=Count("reservas")).order_by("-total_reservas")[:top]


# 4) AGGREGATE

def ocupacion_total_por_dia(fecha):
    """
    Devuelve el total de franjas reservadas en un día concreto.
    """

    return Booking.objects.filter(fecha=fecha,estado__in=["pendiente","confirmada"]).aggregate(total_franjas=Count("franjas", distinct=True))

def franjas_reservas_por_sala(espacio):
    """
    Devuelve el total de franjas reservadas por un espacioen concreto.
    """

    return Booking.objects.filter(espacio=espacio, estado__in=["pendiente","confirmada"]).aggregate(total_franjas=Count("franjas", distinct=True))


# 5) OPTIMIZACIÓN

def reservas_optimizadas():
    """
    Devuelve reservas optimizadas para listado y detalles
    select_related > FK
    prefetch_related > M2M
    """

    return Booking.objects.select_related("cliente","espacio","tarifa").prefetch_related("franjas")


