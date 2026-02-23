from django.shortcuts import render


# Create your views here.
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from .models import Space, TimeSlot, Booking
from .forms import SpaceForm, BookingForm, TimeSlotForm
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required


class SpaceListView(LoginRequiredMixin, ListView):
   model = Space
   template_name = "spaces/list.html"
   context_object_name = "spaces"


   def get_queryset(self):
       queryset = Space.objects.all()
       capacidad = self.request.GET.get("capacidad")
       recurso = self.request.GET.get("recurso")

       if capacidad:
           queryset = queryset.filter(capacidad__gte=capacidad)
       if recurso:
           queryset = queryset.filter(recursos=recurso)

       return queryset

class SpaceCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
   model = Space
   form_class = SpaceForm
   template_name = "spaces/form.html"
   permission_required = "spaces.add_space"
   success_url = reverse_lazy("space_list")

class SpaceUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
   model = Space
   form_class = SpaceForm
   template_name = "spaces/form.html"
   permission_required = "spaces.change_space"
   success_url = reverse_lazy("space_list")

class SpaceDetailView(LoginRequiredMixin, DetailView):
   model = Space
   template_name = "spaces/detail.html"
   context_object_name = "spaces"




class TimeSlotListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
   model = TimeSlot
   template_name = "timeslots/list.html"
   permission_required = "timeslots.view_timeslot"

class TimeSlotCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
   model = TimeSlot
   form_class = TimeSlotForm
   template_name = "timeslots/form.html"
   permission_required = "timeslots.add_timeslot"
   success_url = reverse_lazy("timeslot_list")

class TimeSlotUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
   model = TimeSlot
   form_class = TimeSlotForm
   template_name = "timeslots/form.html"
   permission_required = "timeslots.change_timeslot"
   success_url = reverse_lazy("timeslot_list")



class BookingListView(LoginRequiredMixin, ListView):
   model = Booking
   template_name = "bookings/list.html"


   def get_queryset(self):
       user = self.request.user
       queryset = Booking.objects.select_related(
           "espacio",
           "cliente",
           "tarifa"
       ).prefetch_related("franjas")


       if not user.is_staff:
           queryset = queryset.filter(cliente=user)


       return queryset


class BookingCreateView(LoginRequiredMixin, CreateView):
   model = Booking
   form_class = BookingForm
   template_name = "bookings/form.html"


   def form_valid(self, form):
       form.instance.cliente = self.request.user
       return super().form_valid(form)






@login_required
def cancelar_reserva(request, pk):
   reserva = get_object_or_404(Booking, pk=pk)

   if request.user != reserva.cliente and not request.user.is_staff:
       return redirect("booking_list")

   reserva.estado = "cancelada"
   reserva.save()

   return redirect("booking_list")