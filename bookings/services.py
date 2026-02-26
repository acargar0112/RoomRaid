from django.db.models import Q, F, Count
from .models import Booking, Space
from django.db.models import Sum
from django.db.models.functions import ExtractMonth
import calendar
from django.contrib.auth import get_user_model
User = get_user_model()

# 1) Q OBJECTS

def buscar_reservas(cliente=None, espacio=None, estado=None, fecha_inicio=None, fecha_fin=None):
    """
    Permite realizar búsquedas avanzadas de reservas combinando varios filtros opcionales.

    - Cliente y espacio
    - Estado.
    - El rango de fechas

    Todos son opcionales.
    """

    qs= Booking.objects.all()

    cliente_id = cliente if cliente not in [None, ""] else None
    espacio_id = espacio if espacio not in [None, ""] else None

    if cliente_id or espacio_id:
        qs = qs.filter(Q(cliente__id=cliente_id) | Q(espacio__id=espacio_id))

    if estado:
        qs = qs.filter(estado=estado)

    if fecha_inicio and fecha_fin:
        qs = qs.filter(fecha__range=(fecha_inicio, fecha_fin))
    elif fecha_inicio:
        qs = qs.filter(fecha__qte=fecha_inicio)
    elif fecha_fin:
        qs = qs.filter(fecha__lte=fecha_fin)

    return qs


def get_filtrar_espacios(self):
    """
    Devuelve espacios filtrados por:
    - Capacidad mínima
    - Activos
    """

    capacidad = self.request.GET.get("capacidad")
    recurso = self.request.GET.get("recurso")

    qs = Space.objects.all()

    if capacidad:
        qs = qs.filter(capacidad__gte=capacidad)

    if recurso:
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

    return Space.objects.annotate(total_franjas=Count("reserva__franjas", distinct=True)).order_by("-total_franjas")


def clientes_con_reservas_activas():
    """
    Devuelve clientes con el número de reservas activas
    """

    return User.objects.annotate(reservas_activas=Count("reserva", filter=Q(reserva__estado="confirmada"))).order_by("-reservas_activas")

def top_salas_mas_usadas(top=5):
    """
    Muestra las salas mas usadas.
    Máximo 5.
    """
    return Space.objects.annotate(total_reservas=Count("reserva")).order_by("-total_reservas")[:top]


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

# CONSULTAS NECESARIAS PARA EL DASHBOARD

def reservas_por_mes():
    """
    Devuelve el número de reservas agrupadas por mes
    """
    return Booking.objects.annotate(mes=ExtractMonth("fecha")).values("mes").annotate(total=Count("id")).order_by("mes")

def total_reservas():
    """
    Devuelve el número total de reservas registradas
    """
    return Booking.objects.filter(estado__in=["pendiente","confirmada"]).count()

def espacio_mas_reservado():
    """
    Devuelve el espacio al cual le han hecho mas reservas.
    """
    return Space.objects.annotate(total=Count("reserva")).order_by("-total").first()

def ingresos_totales():
    """
    Devuelve la suma total de todas las reservas
    """
    return Booking.objects.aggregate(total=Sum("coste_total"))["total"] or 0

# CONSULTA NECESARIA PARA OCCUPANCY

def esta_reservado(espacio_id, franja_id, fecha):
    """
    Devuelve True si existe una reserva para un espacio, franja y fecha.
    """
    return Booking.objects.filter(espacio_id=espacio_id,franjas__id=franja_id,fecha=fecha,estado__in=["pendiente","confirmada"]).exists()