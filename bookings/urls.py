from django.urls import path
from .views import *

urlpatterns = [
    path('', HomeView.as_view(), name="home"),

    # Spaces
    path('spaces/', SpaceListView.as_view(), name="space_list"),
    path('spaces/create/', SpaceCreateView.as_view(), name="space_create"),
    path('spaces/<int:pk>/', SpaceDetailView.as_view(), name="space_detail"),
    path('spaces/<int:pk>/edit/', SpaceUpdateView.as_view(), name="space_update"),
    path('spaces/<int:pk>/delete/', SpaceDeleteView.as_view(), name="space_delete"),

    # TimeSlots
    path('timeslots/', TimeSlotListView.as_view(), name="timeslot_list"),
    path('timeslots/create/', TimeSlotCreateView.as_view(), name="timeslot_create"),
    path('timeslots/<int:pk>/edit/', TimeSlotUpdateView.as_view(), name="timeslot_update"),
    path('timeslots/<int:pk>/delete/', TimeSlotDeleteView.as_view(), name="timeslot_delete"),

    # Rates
    path('rates/', RateListView.as_view(), name='rate_list'),
    path('rates/create/', RateCreateView.as_view(), name='rate_create'),
    path('rates/<int:pk>/', RateDetailView.as_view(), name='rate_detail'),
    path('rates/<int:pk>/edit/', RateUpdateView.as_view(), name='rate_update'),
    path('rates/<int:pk>/delete/', RateDeleteView.as_view(), name='rate_delete'),

    # Bookings
    path('bookings/', BookingListView.as_view(), name='booking_list'),
    path('bookings/create/', BookingCreateView.as_view(), name='booking_create'),
    path('bookings/<int:pk>/', BookingDetailView.as_view(), name='booking_detail'),
    path('bookings/<int:pk>/cancel/', cancelar_reserva, name='booking_cancel'),

    # Stats & Occupancy
    path('stats/', stats_view, name='stats'),
    path('occupancy/', occupancy_view, name='occupancy')
]
