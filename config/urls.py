from django.contrib import admin
from django.urls import path, include
from bookings.views import HomeView

urlpatterns = [
    path('admin/', admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("accounts/", include("django.contrib.auth.urls")),
    path("bookings/", include("bookings.urls")),
    path('', HomeView.as_view(), name="home"),
]
