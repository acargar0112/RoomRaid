from django.utils.deprecation import MiddlewareMixin
from django.utils import timezone
from bookings.models import Booking

class UIPreferenceMiddleware(MiddlewareMixin):
    """
        Sincroniza la preferencia de interfaz entre:
        - Cookie 'ui_pref'
        - Profile.preferencia
        Así el estilo de la página web se cambiará teniendo en cuenta la variable preferencia del perfil que estará sincronizada con la cookie ui_pref
    """
    def process_request(self, request):
        cookie_pref = request.COOKIES.get("ui_pref")

        if request.user.is_authenticated:
            if cookie_pref:
                if request.user.profile.preferencia != cookie_pref:
                    request.user.profile.preferencia = cookie_pref
                    request.user.profile.save()
                request.ui_pref = cookie_pref
            else:
                request.ui_pref = request.user.profile.preferencia
        else:
            request.ui_pref = cookie_pref or "oscuro"


class BookingAuditMiddleware(MiddlewareMixin):
    """
    Registra accesos a creación o cancelación de reservas, mostrando en consola la fecha y hora, usuario, booking, method y path
    """

    def process_view(self, request, view_func, view_args, view_kwargs):
        path = request.path

        if path.startswith("/bookings/bookings/create/") or path.endswith("/cancel/"):

            user = request.user if request.user.is_authenticated else None

            booking_id = view_kwargs.get("pk")
            booking = None
            if booking_id:
                booking = Booking.objects.filter(pk=booking_id).first()

            print(
                f"[AUDIT] {timezone.now()} | "
                f"User: {user} | "
                f"Booking: {booking} | "
                f"Method: {request.method} | "
                f"Path: {path}"
            )

        return None
