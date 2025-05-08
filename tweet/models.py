from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from django.contrib.auth.hashers import make_password, check_password


class Complaint(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('In Progress', 'In Progress'),
        ('Resolved', 'Resolved'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    description = models.TextField()
    address = models.CharField(max_length=255, blank=True, null=True) 
    created_at= models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False) 
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')

    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.status}"


class ComplaintImage(models.Model):
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='complaint_images/')

    def __str__(self):
        return f"Image for Complaint {self.complaint.id}"

class AdminProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='admin_profile')
    # Stores hashed answers for fixed questions
    security_answer_1_hash = models.CharField(max_length=128)  # For "What is your favourite food?"
    security_answer_2_hash = models.CharField(max_length=128)  # For "What is your childhood name?"

    def set_security_answers(self, answer1, answer2):
        self.security_answer_1_hash = make_password(answer1.strip().lower())
        self.security_answer_2_hash = make_password(answer2.strip().lower())
        self.save()

    def check_security_answers(self, answer1, answer2):
        return (
            check_password(answer1.strip().lower(), self.security_answer_1_hash) and
            check_password(answer2.strip().lower(), self.security_answer_2_hash)
        )

