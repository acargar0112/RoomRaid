from django.contrib import admin
from accounts.models import User, Profile

class ProfileInLine(admin.StackedInline):
    """
    Modelo admin para que Profile salga abajo de un perfil creado
    """
    model = Profile
    can_delete = False
    extra = 0

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """
    Modelo admin para User personalizado
    """
    list_display = ("email", "display_name", "activo", "is_staff")
    search_fields = ("email", "display_name")
    list_filter = ("is_staff", "is_active")
    inlines = [ProfileInLine]

    def get_inline_instances(self, request, obj=None):
        """
        Cuando crea un usuario no muestra el inline para Profile, cuando se está editando sí
        """
        if not obj:
            return []
        return super().get_inline_instances(request, obj)

    fieldsets = (
        ("Información de acceso", {
            "fields": ("email",
                       "password")
        }),
        ("Datos personales", {
            "fields": ("username",
                       "display_name")
        }),
        ("Permisos", {
            "fields": ("is_active",
                       "is_staff",
                       "is_superuser",
                       "groups",
                       "user_permissions"),
        }),
        ("Fechas importantes", {
            "fields": ("last_login",
                       "date_joined"),
        }),
    )

    readonly_fields = ("last_login", "date_joined")



@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """
    Modelo admin para Profile personalizado
    """
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