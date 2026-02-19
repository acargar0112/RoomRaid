from django.db import models
from django.conf import settings

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