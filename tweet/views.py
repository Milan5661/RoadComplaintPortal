from django.shortcuts import render
from rest_framework import generics
from .models import Complaint
from .serializers import ComplaintSerializer
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator

def index(request):
    return render(request, 'index.html')

class ComplaintListCreateView(generics.ListCreateAPIView):
    serializer_class = ComplaintSerializer

    def get_queryset(self):
        return Complaint.objects.all().order_by('-date_reported')


@csrf_exempt
def submit_complaint(request):
    if request.method == "POST":
        description = request.POST.get("description")
        image = request.FILES.get("image")
        location = request.POST.get("location")

        if not description or not location:
            return JsonResponse({"error": "Missing required fields"}, status=400)

        complaint = Complaint.objects.create(
            description=description,
            image=image,
            location=location
        )
        return JsonResponse({"message": "Complaint submitted successfully", "id": complaint.id})

    return JsonResponse({"error": "Invalid request method"}, status=405)

# ✅ Fix for missing 'complaints_list' function
def complaints_list(request):
    complaints = Complaint.objects.all().values("id", "description", "image", "location", "created_at")
    return JsonResponse({"complaints": list(complaints)})
