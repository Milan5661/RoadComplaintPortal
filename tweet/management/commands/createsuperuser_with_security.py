from django.core.management.base import CommandError
from django.contrib.auth.management.commands.createsuperuser import Command as CreateSuperuserCommand
from django.db import transaction
from tweet.models import AdminProfile
from django.contrib.auth import get_user_model

class Command(CreateSuperuserCommand):
    help = 'Create a superuser and prompt for security question answers.'

    def handle(self, *args, **options):
        User = get_user_model()
        # Call the original createsuperuser command
        super().handle(*args, **options)
        username = options.get('username')
        if not username:
            username = input('Username: ')
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise CommandError(f"User {username} not found.")
        # Prompt for security answers
        answer1 = input('What is your favourite food? ').strip()
        answer2 = input('What is your childhood name? ').strip()
        # Create or update AdminProfile
        with transaction.atomic():
            profile, _ = AdminProfile.objects.get_or_create(user=user)
            profile.set_security_answers(answer1, answer2)
            print('Security questions saved for admin user.')
