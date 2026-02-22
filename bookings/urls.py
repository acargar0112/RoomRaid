from django.urls import path
from .views import *

urlpatterns = [
    path("", SpaceListView.as_view(), name="space_list"),
    path("create/", SpaceCreateView.as_view(), name="space_create"),
    path("<int:pk>/", SpaceDetailView.as_view(), name="space_detail"),
    path("<int:pk>/edit/", SpaceUpdateView.as_view(), name="space_update"),
    path("", TimeSlotListView.as_view(), name="timeslot_list"),
    path("create/", TimeSlotCreateView.as_view(), name="timeslot_create"),
    path("<int:pk>/edit/", TimeSlotUpdateView.as_view(), name="timeslot_update"),
]
