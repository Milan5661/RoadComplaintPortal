# signals.py
from django.contrib.auth.signals import user_login_failed
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser

@receiver(user_login_failed)
def track_failed_login(sender, credentials, request, **kwargs):
    try:
        user = CustomUser.objects.get(username=credentials['username'])
        user.increment_failed_attempts()
    except CustomUser.DoesNotExist:
        pass
