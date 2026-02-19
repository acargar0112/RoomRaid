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
    - activo (True/False)
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
    Modelo que representa una franja horaria disponible.
    Este modelo tendrá:
    - hora_inicio
    - hora_fin
    - activo (True/False)
    - Funcion clean para hora_fin > hora_inicio
    - Hora inicio y fin unicas
    """
    hora_inicio = models.TimeField(verbose_name="Hora de inicio")
    hora_fin = models.TimeField(verbose_name="Hora de fin")
    activo = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        verbose_name="Franja Horaria"
        verbose_name_plural = "Franjas Horarias"
        ordering = ["hora_inicio"]
        unique_together = ("hora_inicio","hora_fin")

    def __str__(self):
        return f"{self.hora_inicio} - {self.hora_fin}"

    def clean(self):
        if self.hora_fin <= self.hora_inicio:
            raise ValidationError("La hora de fin debe ser mayor que la hora de inicio.")

class Rate(models.Model):
    """
    Modelo que representa a la tarifa.
    Este modelo tendrá:
    - nombre
    - precio
    - activo (True/False)
    - condiciones
    - relacion M2M con space  (espacios)
    - Función clean para limpiar el precio
    - Nombres unicos
    """
    nombre = models.CharField(max_length=100, unique=True, verbose_name="Nombre")
    precio = models.DecimalField(max_digits=6, decimal_places=2, verbose_name="Precio")
    condiciones = models.TextField(max_length=500, blank=True, null=True, verbose_name="Condiciones")
    activo = models.BooleanField(default=True, verbose_name="Activo")
    espacios = models.ManyToManyField(Space, related_name="tarifas",related_query_name="tarifa",verbose_name="Espacios")

    class Meta:
        verbose_name = "Tarifa"
        verbose_name_plural = "Tarifas"
        ordering = ["nombre"]

    def __str__(self):
        return f"{self.nombre} - {self.precio}€"

    def clean(self):
        if self.precio < 0:
            raise ValidationError("El precio tiene que ser mayor a 0.")