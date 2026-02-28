from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    """
    Modelo personalizado de user usando AbstractUser, le añadimos un email y para que se loggee con email
    """
    display_name = models.CharField(max_length=200, blank=True)
    email = models.EmailField(unique=True)
    activo = models.BooleanField(default=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.display_name or self.email

class Profile(models.Model):
    """
    Modelo Perfil para Usuario donde hay información extra
    """
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', related_query_name='profile')
    empresa = models.CharField(max_length=200, blank=True)
    telefono = models.CharField(max_length=30, blank=True)
    preferencia = models.CharField(max_length=200, choices=[
        ("claro", "claro"),
        ("oscuro", "oscuro"),
    ], default="oscuro")

    def __str__(self):
        return f"Perfil de {self.usuario}"