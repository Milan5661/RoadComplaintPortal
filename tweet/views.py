from django.shortcuts import render, redirect
from rest_framework import generics
from .models import Complaint
from .serializers import ComplaintSerializer
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from .forms import ComplaintForm 
import json

# Home Page
def index(request):
    return render(request, 'index.html')

# Complaint Form View (For Web)
def complaint_form(request):
    form = ComplaintForm()
    return render(request, "tweet/complaint_form.html", {"form": form})

# API: List & Create Complaints
class ComplaintListCreateView(generics.ListCreateAPIView):
    serializer_class = ComplaintSerializer

    def get_queryset(self):
        return Complaint.objects.all().order_by('-date_reported')

#  FIXED: Single View for Complaints Submission
@csrf_exempt  # Remove this in production & use proper authentication
def submit_complaint(request):
    if request.method == "POST":
        # Check if request is from a web form or API
        if request.content_type == "application/json":
            try:
                data = json.loads(request.body)
                description = data.get('description')
                location = data.get('location', 'Unknown')
            except json.JSONDecodeError:
                return JsonResponse({"error": "Invalid JSON data"}, status=400)
        else:
            description = request.POST.get("description")
            location = request.POST.get("location", "Unknown")
            image = request.FILES.get("image")  # Get uploaded file
            latitude = request.POST.get("latitude")
            longitude = request.POST.get("longitude")

        # Ensure user is authenticated
        user = request.user if request.user.is_authenticated else None
        if not user:
            return JsonResponse({"error": "User not authenticated"}, status=403)

        # Create Complaint
        complaint = Complaint.objects.create(
            user=user,
            description=description,
            location=location,
            image=image if "image" in request.FILES else None,
            latitude=latitude if latitude else None,
            longitude=longitude if longitude else None
        )
        
        return render(request, "tweet/complaint_success.html", {"complaint_id": complaint.id})

    return JsonResponse({"error": "Invalid request method"}, status=405)

# API: List Complaints
def complaints_list(request):
    complaints = Complaint.objects.all().values("id", "description", "image", "location", "date_reported")
    return JsonResponse({"complaints": list(complaints)})

# User Registration View
def register_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'tweet/register.html', {'form': form})

# 📌 User Login View
def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'tweet/login.html', {'form': form})

# 📌 User Logout View
@login_required
def logout_view(request):
    logout(request)
    return redirect('home')
