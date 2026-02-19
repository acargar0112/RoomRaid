from django.contrib import admin
from bookings.models import Space, TimeSlot

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