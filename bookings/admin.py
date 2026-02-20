from django.contrib import admin
from bookings.models import Space, TimeSlot, Rate, Booking

@admin.register(Space)
class SpaceAdmin(admin.ModelAdmin):
    """
    Modelo para Space en admin
    """
    list_display = ("nombre", "capacidad", "ubicacion", "recursos", "activo", "administrador")
    list_filter = ("nombre", "capacidad", "ubicacion")
    search_fields = ("nombre", "ubicacion")

    fieldsets = [
        ('Datos Generales', {
            'fields': [
                'nombre',
                'capacidad',
                'ubicacion',
                'recursos',
            ],
        }), ("Metadatos", {
            'fields': [
                'activo',
                'administrador',
            ]
        })
    ]

@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    """
    Modelo para TimeSlot en admin
    """
    list_display = ("hora_inicio", "hora_fin", "activo")
    list_filter = ("activo",)

    fieldsets = [
        ('Datos Generales', {
            'fields': [
                'hora_inicio',
                'hora_fin',
            ],
        }), ("Metadatos", {
            'fields': [
                'activo',
            ]
        })
    ]

@admin.register(Rate)
class RateAdmin(admin.ModelAdmin):
    """
    Modelo para Rate en admin
    """
    list_display = ("nombre", "precio", "activo")
    list_filter = ("precio",)
    search_fields = ("nombre",)

    fieldsets = [
        ('Datos Generales', {
            'fields': [
                'nombre',
                'precio',
                'condiciones'
            ],
        }), ("Metadatos", {
            'fields': [
                'activo',
                'espacios'
            ]
        })
    ]

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    """
    Modelo para Booking en admin
    """
    list_display = ("id", "espacio", "cliente", "fecha", "estado", "coste_total")
    list_filter = ("estado", "fecha", "espacio")
    search_fields = ("espacio__nombre",)
    autocomplete_fields = ["espacio", "cliente", "tarifa"]

    fieldsets = [
        ('Datos Generales', {
            'fields': [
                'cliente',
                'espacio',
                'franjas',
                'tarifa',
                'fecha'
            ],
        }), ("Metadatos", {
            'fields': [
                'notas',
                'estado',
                'coste_total',
            ]
        })
    ]






