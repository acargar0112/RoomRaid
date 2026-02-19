from django import forms
from bookings.models import Space, TimeSlot

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

