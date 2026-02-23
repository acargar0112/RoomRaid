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


def es_admin(user):
    return user.groups.filter(name="admin").exists()


class HomeView(TemplateView):
    template_name = "base.html"


class SpaceListView(LoginRequiredMixin, ListView):
   """
    Muestra el listado de todos los espacios registrados en el sistema.
   """
   template_name = "spaces/list.html"
   context_object_name = "spaces"

class SpaceCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
   """
   Permite crear un nuevo espacio (requiere permiso add_space).
   """
   model = Space
   form_class = SpaceForm
   template_name = "spaces/form.html"
   permission_required = "spaces.add_space"
   success_url = reverse_lazy("space_list")


   def dispatch(self, request, *args, **kwargs):
       if not es_admin(request.user):
           raise PermissionDenied
       return super().dispatch(request, *args, **kwargs)

class SpaceUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
   """
   Permite editar un espacio existente (requiere permiso change_space).
   """
   model = Space
   form_class = SpaceForm
   template_name = "spaces/form.html"
   permission_required = "spaces.change_space"
   success_url = reverse_lazy("space_list")

class SpaceDetailView(LoginRequiredMixin, DetailView):
   """
   Muestra el detalle completo de un espacio concreto.
   """
   model = Space
   template_name = "spaces/detail.html"
   context_object_name = "spaces"





class TimeSlotListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
   """
   Muestra el listado de todas las franjas horarias disponibles.
   """
   model = TimeSlot
   template_name = "timeslots/list.html"
   permission_required = "timeslots.view_timeslot"

class TimeSlotCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
   """
   Permite crear una nueva franja horaria (requiere permiso add_timeslot).
   """
   model = TimeSlot
   form_class = TimeSlotForm
   template_name = "timeslots/form.html"
   permission_required = "timeslots.add_timeslot"
   success_url = reverse_lazy("timeslot_list")

class TimeSlotUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
   """
   Permite modificar una franja horaria existente.
   """
   model = TimeSlot
   form_class = TimeSlotForm
   template_name = "timeslots/form.html"
   permission_required = "timeslots.change_timeslot"
   success_url = reverse_lazy("timeslot_list")






class RateListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    """
    Muestra el listado de todas las tarifas disponibles.
    """
    model = Rate
    template_name = "rates/list.html"
    permission_required = "rates.view_rate"

class RateDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    """
    Muestra el detalle de una tarifa específica.
    """
    model = Rate
    template_name = "rates/detail.html"
    permission_required = "rates.view_rate"

class RateCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """
    Permite crear una nueva tarifa asociable a espacios.
    """
    model = Rate
    form_class = RateForm
    template_name = "rates/form.html"
    permission_required = "rates.add_rate"
    success_url = reverse_lazy("rate_list")

class RateUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """
    Permite editar una tarifa existente.
    """
    model = Rate
    form_class = RateForm
    template_name = "rates/form.html"
    permission_required = "rates.change_rate"
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

   def dispatch(self, request, *args, **kwargs):
        if not request.user.groups.filter(name="cliente").exists():
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

   def form_valid(self, form):
        form.instance.cliente = self.request.user
        return super().form_valid(form)

class BookingDetailView(LoginRequiredMixin, DetailView):
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