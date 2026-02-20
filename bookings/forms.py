from django import forms
from bookings.models import Space, TimeSlot, Rate, Booking
from django.utils import timezone


class SpaceForm(forms.ModelForm):
    """
    Form para crear un Modelo Space, con validación para que la capacidad no sea negativa o 0
    """
    class Meta:
        model = Space
        fields = ["nombre", "capacidad", "ubicacion", "recursos", "activo", "administrador"]

    def clean_capacidad(self):
        """
        Validación capacidad
        """
        capacidad = self.cleaned_data["capacidad"]

        if capacidad <= 0:
            raise forms.ValidationError("Capacidad debe ser positivo o mayor que 0")
        return capacidad


class TimeSlotForm(forms.ModelForm):
    """
    Form para crear una Timezone con validación de hora
    """
    class Meta:
        model = TimeSlot
        fields = ["hora_inicio", "hora_fin", "activo"]

    def clean(self):
        """
        Validación hora de inicio anterior a fin
        """
        inicio = self.cleaned_data.get("hora_inicio")
        fin = self.cleaned_data.get("hora_fin")

        if inicio and fin and inicio >= fin:
            raise forms.ValidationError("Hora de inicio debe ser anterior que fin")
        return inicio, fin

class RateForm(forms.ModelForm):
    """
    Form para crear un Rate con validcación de precio
    """
    class Meta:
        model = Rate
        fields = ["nombre", "precio", "condiciones", "activo", "espacios"]

    def clean_precios(self):
        """
        Validación de precio > 0
        """
        precio = self.cleaned_data["precio"]

        if precio <= 0:
            raise forms.ValidationError("Precio debe ser mayor que 0")
        return precio

class BookingForm(forms.ModelForm):
    """
    Form para crear un Booking con validaciones
    """
    franjas = forms.ModelMultipleChoiceField(
        queryset=TimeSlot.objects.filter(activo=True),
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = Booking
        fields = ["espacio", "franjas", "tarifa", "fecha", "notas"]

    def __init__(self, *args, **kwargs):
        """
        Constructor que limita qué tarfias puedes elegir, si eres un cliente solo las activas, si eres admin todas
        """
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if not (self.user and self.user.is_staff):
            self.fields["tarifa"].queryset = Rate.objects.filter(activo=True)

    def clean_fecha(self):
        """
        Validacion de fechas para que no sean anterior a hoy
        """
        fecha = self.cleaned_data["fecha"]
        if fecha < timezone.localdate():
            raise forms.ValidationError("No puedes reservar fechas pasadas")
        return fecha

    def clean_franja(self):
        """
        Validacion de franjas horarias para que tengan que seleccionar 1 y sigan un bloque continuo (Ej: 09:00 - 10:00, 10:00 - 11:00, 11:00 - 12:00)
        """
        franja = self.cleaned_data["franjas"]
        if not franja:
            raise forms.ValidationError("Selecciona una franja")
        ordered = sorted(franja, key=lambda f: f.hora_inicio)
        for i in range(len(ordered) - 1):
            if ordered[1].hora_fin != ordered[i + 1].hora_inicio:
                raise forms.ValidationError("Las franjas deben formar un bloque continuo")
            return franja

    def clean(self):
        """
        Validación global para que no falte nada y busque si ya existe una reserva con la misma franja horaria
        """
        cleaned = super().clean()
        espacio = cleaned.get("espacio")
        fecha = cleaned.get("fecha")
        franja = cleaned.get("franjas")
        if not (espacio and fecha and franja):
            return cleaned

        existe = Booking.objects.filter(
            espacio=espacio,
            fecha=fecha,
            estado__in=["pendiente", "confirmada"]
        ).filter(franjas__in=franja).distinct()

        if existe.exists():
            raise forms.ValidationError("Algunas de las franjas horarias ya están reservadas para esta sala")
        return cleaned



