from django.contrib import admin
from accounts.models import User, Profile

class ProfileInLine(admin.StackedInline):
    """
    Modelo admin para que Profile salga abajo de un perfil creado
    """
    model = Profile
    can_delete = False

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """
    Modelo admin para Usuario personalizado
    """
    list_display = ("email", "display_name", "activo", "is_staff")
    search_fields = ("email", "display_name")
    list_filter = ("is_staff", "is_active")
    inlines = [ProfileInLine]


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("usuario", "empresa", "telefono", "preferencia")
    search_fields = ("usuario__email", "empresa")

    fieldsets = [
        ('Datos Generales', {
            'fields': [
                'usuario',
                'empresa',
                'telefono',
            ],
        }), ("Preferencias de UI", {
            'fields': [
                'preferencia',
            ]
        })
    ]