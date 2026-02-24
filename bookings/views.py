from django.shortcuts import render, get_object_or_404, redirect
import calendar

from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.urls import reverse_lazy
from django.utils.dateparse import parse_date

from core.mixins import AdminOnlyMixin, OwnerOrAdminBookingMixin
from .models import Space, TimeSlot, Booking, Rate
from .forms import SpaceForm, BookingForm, TimeSlotForm, RateForm
from .services import (
    buscar_reservas,
    filtrar_espacios,
    reservas_optimizadas,
    incrementar_contador_reservas,
    ocupacion_total_por_dia,
    reservas_por_mes,
    total_reservas,
    espacio_mas_reservado,
    ingresos_totales,
    esta_reservado,
)


class HomeView(TemplateView):
    template_name = "base.html"


class SpaceListView(AdminOnlyMixin, ListView):
    """
    Muestra el listado de todos los espacios registrados en el sistema.
    Permite filtrar por capacidad mínima o recurso (Q objects).
    """
    model = Space
    template_name = "spaces/list.html"
    context_object_name = "spaces"

    def get_queryset(self):
        capacidad = self.request.GET.get("capacidad")
        recurso = self.request.GET.get("recurso")

        return filtrar_espacios(
            capacidad_minima=capacidad,
            recurso=recurso
        )


class SpaceCreateView(AdminOnlyMixin, CreateView):
   """
   Permite crear un nuevo espacio (requiere permiso add_space).
   """
   model = Space
   form_class = SpaceForm
   template_name = "spaces/form.html"
   success_url = reverse_lazy("space_list")


class SpaceUpdateView(AdminOnlyMixin, UpdateView):
   """
   Permite editar un espacio existente (requiere permiso change_space).
   """
   model = Space
   form_class = SpaceForm
   template_name = "spaces/form.html"
   success_url = reverse_lazy("space_list")


class SpaceDeleteView(AdminOnlyMixin, DeleteView):
   """
   Permite eliminar un espacio existente.
   """
   model = Space
   template_name = "spaces/delete.html"
   success_url = reverse_lazy("space_list")


class SpaceDetailView(AdminOnlyMixin, DetailView):
   """
   Muestra el detalle completo de un espacio concreto.
   """
   model = Space
   template_name = "spaces/detail.html"
   context_object_name = "spaces"





class TimeSlotListView(AdminOnlyMixin, ListView):
   """
   Muestra el listado de todas las franjas horarias disponibles.
   """
   model = TimeSlot
   template_name = "timeslots/list.html"
   context_object_name = "timeslots"


class TimeSlotCreateView(AdminOnlyMixin, CreateView):
   """
   Permite crear una nueva franja horaria (requiere permiso add_timeslot).
   """
   model = TimeSlot
   form_class = TimeSlotForm
   template_name = "timeslots/form.html"
   success_url = reverse_lazy("timeslot_list")


class TimeSlotUpdateView(AdminOnlyMixin, UpdateView):
   """
   Permite modificar una franja horaria existente.
   """
   model = TimeSlot
   form_class = TimeSlotForm
   template_name = "timeslots/form.html"
   success_url = reverse_lazy("timeslot_list")


class TimeSlotDeleteView(AdminOnlyMixin, DeleteView):
   """
   Permite eliminar una franja horaria existente.
   """
   model = TimeSlot
   template_name = "timeslots/delete.html"
   success_url = reverse_lazy("timeslot_list")






class RateListView(AdminOnlyMixin, ListView):
    """
    Muestra el listado de todas las tarifas disponibles.
    """
    model = Rate
    template_name = "rates/list.html"
    context_object_name = "rates"


class RateDetailView(AdminOnlyMixin, DetailView):
    """
    Muestra el detalle de una tarifa específica.
    """
    model = Rate
    template_name = "rates/detail.html"


class RateCreateView(AdminOnlyMixin, CreateView):
    """
    Permite crear una nueva tarifa asociable a espacios.
    """
    model = Rate
    form_class = RateForm
    template_name = "rates/form.html"
    success_url = reverse_lazy("rate_list")


class RateUpdateView(AdminOnlyMixin, UpdateView):
    """
    Permite editar una tarifa existente.
    """
    model = Rate
    form_class = RateForm
    template_name = "rates/form.html"
    success_url = reverse_lazy("rate_list")


class RateDeleteView(AdminOnlyMixin, DeleteView):
    """
    Permite eliminar una tarifa existente.
    """
    model = Rate
    template_name = "rates/delete.html"
    success_url = reverse_lazy("rate_list")




class BookingListView(LoginRequiredMixin, ListView):
    """
    Muestra el listado de reservas del sistema (o del usuario autenticado).
    Permite búsqueda avanzada usando Q objects.
    """
    model = Booking
    template_name = "bookings/list.html"
    context_object_name = "bookings"

    def get_queryset(self):
        cliente = self.request.GET.get("cliente")
        espacio = self.request.GET.get("espacio")
        estado = self.request.GET.get("estado")
        fecha_inicio = self.request.GET.get("fecha_inicio")
        fecha_fin = self.request.GET.get("fecha_fin")

        qs = buscar_reservas(
            cliente=cliente,
            espacio=espacio,
            estado=estado,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin
        )

        if self.request.user.is_staff:
            return qs

        return qs.filter(cliente=self.request.user)

class BookingCreateView(LoginRequiredMixin, CreateView):
    """
    Permite crear una nueva reserva asignando automáticamente el cliente autenticado.
    Incrementa el contador de reservas del espacio (F expression).
    """
    model = Booking
    form_class = BookingForm
    template_name = "bookings/form.html"
    success_url = reverse_lazy("booking_list")

    def dispatch(self, request, *args, **kwargs):
        es_cliente = request.user.groups.filter(name="cliente").exists()
        es_admin = request.user.is_staff

        if not (es_cliente or es_admin):
            raise PermissionDenied

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.cliente = self.request.user
        response = super().form_valid(form)

        # F expression
        incrementar_contador_reservas(form.instance.espacio)

        return response

class BookingDetailView(OwnerOrAdminBookingMixin, DetailView):
    """
    Muestra el detalle completo de una reserva específica.
    Usa consultas optimizadas.
    """
    template_name = "bookings/detail.html"

    def get_queryset(self):
        qs = reservas_optimizadas()

        if self.request.user.is_staff:
            return qs

        return qs.filter(cliente=self.request.user)





@login_required
def cancelar_reserva(request, pk):
   """
   Permite cancelar una reserva si el usuario es el cliente o es administrador.
   """
   reserva = get_object_or_404(Booking, pk=pk)

   if not request.user.is_staff and reserva.cliente != request.user:
       raise PermissionDenied

   reserva.estado = "cancelada"
   reserva.save()

   return redirect("booking_list")


@login_required
def stats_view(request):
    """
    Muestra estadísticas globales del sistema.
    Solo accesible para ADMIN.
    """
    if not request.user.is_staff:
        raise PermissionDenied

    total = total_reservas()

    espacio_top_obj = espacio_mas_reservado()
    espacio_top = espacio_top_obj.nombre if espacio_top_obj else "Sin datos"

    ingresos = ingresos_totales() or 0

    reservas_mes_qs = reservas_por_mes()
    reservas_mes_dict = {}
    for item in reservas_mes_qs:
        numero_mes = item["mes"]
        cantidad = item["total"]
        nombre_mes = calendar.month_name[numero_mes] if numero_mes else "Sin mes"
        reservas_mes_dict[nombre_mes] = cantidad

    context = {
        "total_reservas": total,
        "espacio_top": espacio_top,
        "ingresos_totales": ingresos,
        "reservas_por_mes": reservas_mes_dict,
    }

    return render(request, "stats/dashboard.html", context)


@login_required
def occupancy_view(request):
    """
    Muestra la ocupación total de franjas reservadas
    para una fecha seleccionada.
    """
    if not request.user.is_staff:
        raise PermissionDenied

    fecha = request.GET.get("fecha")
    context = {
        "ocupacion": {},  # SIEMPRE existe
    }

    if fecha:
        fecha_parseada = parse_date(fecha)

        espacios = Space.objects.filter(activo=True).order_by("nombre")
        franjas = TimeSlot.objects.all().order_by("hora_inicio")

        ocupacion = {}
        for espacio in espacios:
            ocupacion[espacio.id] = {}
            for franja in franjas:
                ocupado = esta_reservado(espacio.id, franja.id, fecha_parseada)
                ocupacion[espacio.id][franja.id] = ocupado

        resultado = ocupacion_total_por_dia(fecha_parseada)
        total_franjas = resultado.get("total_franjas", 0)

        context.update({
            "fecha": fecha_parseada,
            "espacios": espacios,
            "franjas": franjas,
            "ocupacion": ocupacion,
            "total_franjas": total_franjas,
        })

    return render(request, "occupancy/day.html", context)

