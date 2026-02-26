from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import Http404
from bookings.models import Booking

class AdminOnlyMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    Mixin personalizado que solo permite acceso a usuarios staff (admin). Si no es admin hace un raise de 404
    """
    def test_func(self):
        """
        Función que detecta si el user es admin con el is_staff
        """
        return self.request.user.is_staff

    def handle_no_permission(self):
        """
        Si no es admin hace raise de un error forbidden 404
        """
        raise Http404

class OwnerOrAdminBookingMixin(LoginRequiredMixin):
    """
    Mixin personalizado para que solo el creador de una reserva o admin pueda ver los detalles de su reserva, y no otros usuarios. Esto se hace por sentido común, un cliente no debe ver las reservas de otros clientes, pero un admin debe ver todas
    """
    def dispatch(self, request, *args, **kwargs):
        booking = Booking.objects.select_related("cliente").filter(pk=kwargs.get("pk")).first()
        if not booking:
            raise Http404
        if not (request.user.is_staff or booking.cliente_id == request.user.id):
            raise Http404
        self.booking = booking
        return super().dispatch(request, *args, **kwargs)

