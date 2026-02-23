from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, Profile

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    """
    Signal para crear un perfil vacío cuando se cree un usuario
    """
    if created:
        Profile.objects.create(usuario=instance)

@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    """
    Signal para guardar el perfil vacío para el usuario recien creado
    """
    instance.profile.save()
