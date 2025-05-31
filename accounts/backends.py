from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.core.cache import cache

User = get_user_model()

class UserTypeBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, user_type=None, **kwargs):
        if username is None or password is None or user_type is None:
            return None

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return None

        if user.check_password(password):
            # Validate user type
            if user_type == 'admin' and not user.is_superuser:
                return None
            if user_type == 'user' and user.is_superuser:
                return None

            # Store user type in cache
            cache_key = f'user_type_{user.id}'
            cache.set(cache_key, user_type, 3600)  # 1 hour expiry

            return user
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None 