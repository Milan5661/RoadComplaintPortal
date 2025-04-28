from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.shortcuts import render
from .models import CustomUser

class CustomAuthenticationBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = CustomUser.objects.get(username=username)
            
            # Check if login attempts exceed 5
            if user.failed_login_attempts >= 5:
                # Return the user object here; redirection will happen in the view
                return user

            else:
                # Normal authentication (when failed attempts are less than 5)
                if user.check_password(password):
                    user.reset_failed_attempts()
                    return user
                else:
                    user.increment_failed_attempts()
                    raise ValidationError('Incorrect password, please try again.')

        except CustomUser.DoesNotExist:
            return None
