# Debugged and Integrated Code for Road Complaint Portal

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
from django.contrib import messages

# Home Page
def index(request):
    return render(request, 'base.html')

# Complaint Form View (For Web)
@login_required  # Ensures user must be logged in
def complaint_form(request):
    if request.method == "POST":
        form = ComplaintForm(request.POST, request.FILES)
        if form.is_valid():
            # Don't save to DB yet
            complaint = form.save(commit=False)
            # Assign the logged-in user
            complaint.user = request.user
            # Now save
            complaint.save()
            return redirect("complaints_list")  # Or wherever you want to redirect
    else:
        form = ComplaintForm()

    return render(request, "complaint_form.html", {"form": form})

# API: List & Create Complaints
class ComplaintListCreateView(generics.ListCreateAPIView):
    queryset = Complaint.objects.all().order_by('-date_reported')
    serializer_class = ComplaintSerializer

# Complaint Submission


@login_required  # Ensures user must be logged in to submit a complaint
def submit_complaint(request):
    if request.method == "POST":
        description = request.POST.get("description")
        image = request.FILES.get("image")

        if not description or not image:
            return render(request, "complaint_form.html", {"error": "All fields are required."})

        # Create and save complaint with logged-in user
        complaint = Complaint(
            user=request.user,  # Assign current logged-in user
            description=description,
            image=image
        )
        complaint.save()
        return redirect("complaints_list")  # Redirect to complaints list after submission

    return render(request, "complaint_form.html")

# API: List Complaints
def complaints_list(request):
    complaints = Complaint.objects.all().order_by("date_reported")  # Fetch all complaints (latest first)
    return render(request, "complaints_list.html", {"complaints": complaints})

# User Registration View
def register_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('base')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

# User Login View
def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('base')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

# User Logout View
@login_required
def logout_view(request):
    logout(request)
    return redirect('home')

# View for displaying complaints
def complaints_view(request):
    complaints = Complaint.objects.all()
    return render(request, 'complaints.html', {'complaints': complaints})

# Homepage
def home(request):
    return render(request, 'home.html')

def complaints(request):
    all_complaints = Complaint.objects.all()
    return render(request, "complaints.html", {"complaints": all_complaints})

@login_required
def dashboard(request):
    user_complaints = Complaint.objects.filter(user=request.user)
    
    total_complaints = user_complaints.count()
    resolved_complaints = user_complaints.filter(status="Resolved").count()
    pending_complaints = user_complaints.filter(status="Pending").count()

    context = {
        "complaints": user_complaints,
        "total_complaints": total_complaints,
        "resolved_complaints": resolved_complaints,
        "pending_complaints": pending_complaints,
    }
    return render(request, "dashboard.html", context)
