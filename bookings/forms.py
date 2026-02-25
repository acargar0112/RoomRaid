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
        widgets = {
            "nombre": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Nombre del espacio"
            }),
            "capacidad": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Capacidad máxima"
            }),
            "ubicacion": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Ubicación del espacio"
            }),
            "recursos": forms.Select(attrs={
                "class": "form-control",
                "placeholder": "Recursos disponibles",
            }),
            "activo": forms.CheckboxInput(attrs={
                "class": "form-check-input"
            }),
            "administrador": forms.Select(attrs={
                "class": "form-select"
            }),
        }

    def clean_capacidad(self):
        """
        Función para validar la capacidad pasitiva a mayor que 0
        """
        capacidad = self.cleaned_data["capacidad"]
        if capacidad <= 0:
            raise forms.ValidationError("Capacidad debe ser positiva o mayor que 0")
        return capacidad



class TimeSlotForm(forms.ModelForm):
    """
    Form para crear una Timezone con validación de hora
    """
    class Meta:
        model = TimeSlot
        fields = ["hora_inicio", "hora_fin", "activo"]
        widgets = {
            "hora_inicio": forms.TimeInput(attrs={
                "class": "form-control",
                "type": "time"
            }),
            "hora_fin": forms.TimeInput(attrs={
                "class": "form-control",
                "type": "time"
            }),
            "activo": forms.CheckboxInput(attrs={
                "class": "form-check-input"
            }),
        }

    def clean(self):
        """
        Validación hora de inicio anterior a fin
        """
        cleaned = super().clean()
        inicio = cleaned.get("hora_inicio")
        fin = cleaned.get("hora_fin")

        if inicio and fin and inicio >= fin:
            raise forms.ValidationError("Hora de inicio debe ser anterior que fin")

        return cleaned


class RateForm(forms.ModelForm):
    """
    Form para crear un Rate con validación de precio y filtrado de espacios activos.
    """
    class Meta:
        model = Rate
        fields = ["nombre", "precio", "condiciones", "activo", "espacios"]
        widgets = {
            "nombre": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Nombre de la tarifa"
            }),
            "precio": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Precio en euros",
                "min": "0",
                "step": "0.01"
            }),
            "condiciones": forms.Textarea(attrs={
                "class": "form-control",
                "placeholder": "Condiciones de la tarifa",
                "rows": 3
            }),
            "activo": forms.CheckboxInput(attrs={
                "class": "form-check-input"
            }),
            "espacios": forms.SelectMultiple(attrs={
                "class": "form-select"
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["espacios"].queryset = Space.objects.filter(activo=True)

    def clean_precio(self):
        """
        Validación de precio > 0
        """
        precio = self.cleaned_data["precio"]

        if precio <= 0:
            raise forms.ValidationError("El precio debe ser mayor que 0")
        return precio



class BookingForm(forms.ModelForm):
    """
    Form para crear un Booking con validaciones
    """

    franjas = forms.ModelMultipleChoiceField(
        queryset=TimeSlot.objects.filter(activo=True),
        widget=forms.CheckboxSelectMultiple,
        label="Franjas"
    )

    class Meta:
        model = Booking
        fields = ["espacio" ,"tarifa", "fecha", "notas","franjas"]
        widgets = {
            "espacio": forms.Select(attrs={
                "class": "form-select"
            }),
            "tarifa": forms.Select(attrs={
                "class": "form-select"
            }),
            "fecha": forms.DateInput(attrs={
                "class": "form-control",
                "type": "date"
            }),
            "notas": forms.Textarea(attrs={
                "class": "form-control",
                "placeholder": "Notas adicionales",
                "rows": 3
            }),
        }

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

    def clean_franjas(self):
        """
        Validacion de franjas horarias para que tengan que seleccionar 1 y sigan un bloque continuo (Ej: 09:00 - 10:00, 10:00 - 11:00, 11:00 - 12:00)
        """
        franja = self.cleaned_data.get("franjas")
        if not franja:
            raise forms.ValidationError("Selecciona al menos una franja")

        ordered = sorted(franja, key=lambda f: f.hora_inicio)
        for i in range(len(ordered) - 1):
            if ordered[i].hora_fin != ordered[i + 1].hora_inicio:
                raise forms.ValidationError("Las franjas deben formar un bloque continuo")

        return franja

    def clean(self):
        """
        Validación global para que no falte nada (espacio, fechas, franjas), que no formen bloque continuo, que no haya otra reserva en el mismo espacio, fecha y franja, y para que un usuario no pueda tener más de una reserva el mismo día
        """
        cleaned = super().clean()
        espacio = cleaned.get("espacio")
        fecha = cleaned.get("fecha")
        franjas = cleaned.get("franjas")

        if not (espacio and fecha and franjas):
            return cleaned

        existe = Booking.objects.filter(
            espacio=espacio,
            fecha=fecha,
            estado__in=["pendiente", "confirmada"]
        ).filter(franjas__in=franjas).distinct()

        if existe.exists():
            raise forms.ValidationError(
                "Algunas de las franjas horarias ya están reservadas para esta sala"
            )

        if self.user:
            ya_tiene = Booking.objects.filter(
                cliente=self.user,
                fecha=fecha,
                estado__in=["pendiente", "confirmada"]
            ).exists()

            if ya_tiene:
                raise forms.ValidationError(
                    "Ya tienes una reserva para este día. No puedes crear más de una."
                )

        return cleaned




