from django.shortcuts import render

# Create your views here.
complaints = Complaint.objects.all().values("id", "description", "image", "location", "date_reported")
