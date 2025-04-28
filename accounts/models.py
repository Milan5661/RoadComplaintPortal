from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    # Security Questions
    security_question_1 = models.CharField(max_length=255, blank=True, null=True)
    security_answer_1 = models.CharField(max_length=255, blank=True, null=True)
    security_question_2 = models.CharField(max_length=255, blank=True, null=True)
    security_answer_2 = models.CharField(max_length=255, blank=True, null=True)

    # Track failed login attempts
    failed_login_attempts = models.PositiveIntegerField(default=0)

    def reset_failed_attempts(self):
        self.failed_login_attempts = 0
        self.save(update_fields=['failed_login_attempts'])

    def increment_failed_attempts(self):
        self.failed_login_attempts += 1
        self.save(update_fields=['failed_login_attempts'])
