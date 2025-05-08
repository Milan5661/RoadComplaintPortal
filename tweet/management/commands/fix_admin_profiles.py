from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from tweet.models import AdminProfile

class Command(BaseCommand):
    help = 'Ensure all superusers have an AdminProfile and set security questions if missing.'

    def handle(self, *args, **options):
        User = get_user_model()
        superusers = User.objects.filter(is_superuser=True)
        for user in superusers:
            profile, created = AdminProfile.objects.get_or_create(user=user)
            if created or not (profile.security_answer_1_hash and profile.security_answer_2_hash):
                self.stdout.write(self.style.WARNING(f'Set security questions for admin: {user.username}'))
                answer1 = input(f"Enter answer for 'What is your favourite food?' for {user.username}: ").strip()
                answer2 = input(f"Enter answer for 'What is your childhood name?' for {user.username}: ").strip()
                profile.set_security_answers(answer1, answer2)
                self.stdout.write(self.style.SUCCESS(f'Security questions set for admin: {user.username}'))
            else:
                self.stdout.write(self.style.SUCCESS(f'AdminProfile OK for {user.username}'))
        self.stdout.write(self.style.SUCCESS('All superusers have AdminProfile and security questions.'))
