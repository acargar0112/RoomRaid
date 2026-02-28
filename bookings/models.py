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
    contador_reservas = models.PositiveIntegerField(default=0)
    RECURSOS_OPCIONALES = [
        ("proyector", "Proyector"),
        ("pizarra", "Pizarra"),
        ("tv", "Televisión"),
        ("hdmi", "HDMI"),
        ("aire_acondi", "Aire acondicionado"),
    ]
    recursos = models.CharField(max_length=50, choices=RECURSOS_OPCIONALES, verbose_name="Recursos")
    activo = models.BooleanField(default=True, verbose_name="Activo")
    administrador = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Administrador", related_name="espacios_administrados", related_query_name="espacio_administrado")

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

class Booking(models.Model):
    """
    Modelo que representa la reserva completa realizada por un cliente.
    Booking tiene:
    - Relación con cliente, espacio (Space), franjas horarias (TimeSlot), tarifas aplicadas (Rate)
    - Fecha
    - Estado (pendiente, confirmada y cancelada)
    - Notas
    - Coste_total

    Justificación on_delete:

    - Si se elimina un espacio, no puede tener reservas asociadas; si las tiene, no se podrá eliminar. PROTECT
    - Si se elimina un usuario, lo mantenemos y para ello utilizamos SET_NULL, ya que representa un registro del sistema.
    - Si se elimina una tarifa, conservamos el precio y para ello utilizamos SET_NULL. Siempre se conservará la tarifa original aunque esta sea eliminada o modificada.
    """

    ESTADOS = [
        ("pendiente","Pendiente"),
        ("confirmada","Confirmada"),
        ("cancelada","Cancelada"),
    ]

    cliente = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,null=True,blank=True,related_name="reservas", related_query_name="reserva",verbose_name="Cliente")
    espacio = models.ForeignKey(Space,on_delete=models.PROTECT,related_name="reservas",related_query_name="reserva",verbose_name="Espacio")
    franjas = models.ManyToManyField(TimeSlot,related_name="reservas",related_query_name="reserva",verbose_name="Franjas horarias")
    tarifa = models.ForeignKey(Rate,on_delete=models.SET_NULL,null=True,blank=True,related_name="reservas",related_query_name="reserva",verbose_name="Tarifa")
    fecha = models.DateField(verbose_name="Fecha")
    estado = models.CharField(max_length=20,choices=ESTADOS,default="pendiente",verbose_name="Estado")
    notas = models.TextField(max_length=500,blank=True,null=True,verbose_name="Notas")
    coste_total = models.DecimalField(max_digits=7,decimal_places=2,null=True,blank=True,verbose_name="Coste total")

    class Meta:
        verbose_name = "Reserva"
        verbose_name_plural = "Reservas"
        ordering = ["fecha", "espacio"]
        unique_together = ("cliente","espacio","fecha")

    def __str__(self):
        return f"Reserva de: {self.cliente} | Espacio: {self.espacio} | Fecha: {self.fecha}"

