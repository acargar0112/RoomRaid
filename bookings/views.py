from django.shortcuts import render


# Create your views here.
from django.views.generic import ListView, CreateView, UpdateView, DetailView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from .models import Space, TimeSlot, Booking, Rate
from .forms import SpaceForm, BookingForm, TimeSlotForm, RateForm
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from core.mixins import AdminOnlyMixin, OwnerOrAdminBookingMixin


def es_admin(user):
    return user.groups.filter(name="admin").exists()


class HomeView(TemplateView):
    template_name = "base.html"


class SpaceListView(LoginRequiredMixin, ListView):
   """
    Muestra el listado de todos los espacios registrados en el sistema.
   """
   model = Space
   template_name = "spaces/list.html"
   context_object_name = "spaces"

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

class SpaceDetailView(LoginRequiredMixin, DetailView):
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






class RateListView(AdminOnlyMixin, ListView):
    """
    Muestra el listado de todas las tarifas disponibles.
    """
    model = Rate
    template_name = "rates/list.html"

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




class BookingListView(LoginRequiredMixin, ListView):
   """
   Muestra el listado de reservas del sistema (o del usuario autenticado).
   """
   model = Booking
   template_name = "bookings/list.html"

   def get_queryset(self):
      qs = Booking.objects.all()

      if es_admin(self.request.user):
        return qs
      return qs.filter(cliente=self.request.user)

class BookingCreateView(LoginRequiredMixin, CreateView):
   """
   Permite crear una nueva reserva asignando automáticamente el cliente autenticado.
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
        return super().form_valid(form)

class BookingDetailView(OwnerOrAdminBookingMixin, DetailView):
    """
    Muestra el detalle completo de una reserva específica.
    """
    model = Booking
    template_name = "bookings/detail.html"

    def get_queryset(self):
        qs = Booking.objects.all()

        if es_admin(self.request.user):
            return qs
        return qs.filter(cliente=self.request.user)





@login_required
def cancelar_reserva(request, pk):
   """
   Permite cancelar una reserva si el usuario es el cliente o es administrador.
   """
   reserva = get_object_or_404(Booking, pk=pk)

   if not es_admin(request.user) and reserva.cliente != request.user:
       raise PermissionDenied

   reserva.estado = "cancelada"
   reserva.save()

   return redirect("booking_list")