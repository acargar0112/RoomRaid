from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError

class  Space(models.Model):
    """
    Modelo que representa una sala o un espacio reservable dentro de nuestra app.
    Este modelo tendrá:
    - nombre (único)
    - capacidad
    - ubicacion (Zona donde esta)
    - recursos (Recursos disponibles en el espacio | CHOICES)
    - Estado (Activo/inactivo)
    - Administrador (Necesario Rol 2 para la total implementación)
    """
    nombre = models.CharField(max_length=150, unique=True, verbose_name="Nombre")
    capacidad = models.PositiveIntegerField(verbose_name="Capacidad")
    ubicacion = models.CharField(max_length=150,verbose_name="Ubicacion")
    RECURSOS_OPCIONALES = [
        ("proyector", "Proyector"),
        ("pizarra", "Pizarra"),
        ("tv", "Televisión"),
        ("hdmi", "HDMI"),
        ("aire_acondi", "Aire acondicionado"),
    ]
    recursos = models.CharField(max_length=50, choices=RECURSOS_OPCIONALES, verbose_name="Recursos")
    activo = models.BooleanField(default=True, verbose_name="Activo")
    # Administrator requiere aportación del Rol 2
    administrador = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Administrador")

    class Meta:
        verbose_name = "Espacio"
        verbose_name_plural= "Espacios"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class TimeSlot(models.Model):
    """
    Modelo que representa una franja horaria disponible, con relacion con un espacio en concreto.
    Este modelo tendrá:
    - fecha
    - hora_inicio
    - hora_fin
    - estado (activo/inactivo)
    - relación con el modelo Space
    """
    espacio = models.ForeignKey(Space, on_delete=models.CASCADE, related_name="franjas",verbose_name="Espacio")
    fecha = models.DateField(verbose_name="Fecha")
    hora_inicio = models.TimeField(verbose_name="Hora de inicio")
    hora_fin = models.TimeField(verbose_name="Hora de fin")
    activo = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        verbose_name="Franja Horaria"
        verbose_name_plural = "Franjas Horarias"
        ordering = ["fecha", "hora_inicio"]
        unique_together = ("espacio","fecha","hora_inicio","hora_fin")

    def __str__(self):
        return f"{self.espacio.nombre} | {self.fecha} | ({self.hora_inicio}-{self.hora_fin})"

    def clean(self):
        if self.hora_fin <= self.hora_inicio:
            raise ValidationError("La hora de fin debe ser mayor que la hora de inicio.")
