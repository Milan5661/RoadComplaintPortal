from django.db import models

class Complaint(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='complaint_images/', null=True, blank=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    date_reported = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
