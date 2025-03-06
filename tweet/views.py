from django.shortcuts import render, redirect
from rest_framework import generics
from .models import Complaint
from .serializers import ComplaintSerializer
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from .forms import ComplaintForm
from django.contrib import messages
from django.http import JsonResponse

# 🌍 Home Page
def index(request):
    return render(request, 'base.html')

#Complaint Form
@login_required
def complaint_form(request):
    form = ComplaintForm()

    if request.method == "POST":
        form = ComplaintForm(request.POST, request.FILES)
        if form.is_valid():
            complaint = form.save(commit=False)
            complaint.user = request.user
            complaint.save()
            messages.success(request, "Complaint submitted successfully!")
            return redirect("tweet:complaints-list")
        else:
            messages.error(request, "Error submitting complaint. Please try again.")

    return render(request, "complaint_form.html", {"form": form})

#Submit Complaint with Geolocation
@login_required
def submit_complaint(request):
    if request.method == "POST":
        description = request.POST.get("description")
        image = request.FILES.get("image")
        address=request.FILES.get("address")
        latitude = request.POST.get("latitude")
        longitude = request.POST.get("longitude")

        if not description or not image:
            return render(request, "complaint_form.html", {"error": "All fields are required."})

        # Save complaint with location data
        complaint = Complaint(
            user=request.user,
            description=description,
            image=image,
            address=address,
            latitude=latitude,
            longitude=longitude
        )
        complaint.save()
        return redirect("tweet:complaints-list")

    return render(request, "complaint_form.html")

# 🔍 View Complaints
def complaints_list(request):
    complaints = Complaint.objects.all().order_by('-date_reported')
    return render(request, "complaints_list.html", {"complaints": complaints})

# User Authentication Views
def register_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    return redirect('home')

# Dashboard for Users
@login_required
def dashboard(request):
    user_complaints = Complaint.objects.filter(user=request.user)
    
    total_complaints = user_complaints.count()
    resolved_complaints = user_complaints.filter(status="Resolved").count()
    pending_complaints = user_complaints.filter(status="Pending").count()

    complaints = {
        "complaints": user_complaints,
        "total_complaints": total_complaints,
        "resolved_complaints": resolved_complaints,
        "pending_complaints": pending_complaints,
    }
    return render(request, "dashboard.html", {'complaints': complaints})

def home(request):
    return render(request, "home.html")

def get_complaints(request):
    complaints = list(Complaint.objects.values("latitude", "longitude", "description"))
    return JsonResponse(complaints, safe=False)

class ComplaintListCreateView(generics.ListCreateAPIView):
    queryset = Complaint.objects.all().order_by('-date_reported')
    serializer_class = ComplaintSerializer
from django.shortcuts import render


# Hide header/footer for login, register, and logout pages
def login_view(request):
    return render(request, 'login.html', {'exclude_header_footer': True})

def register_view(request):
    return render(request, 'register.html', {'exclude_header_footer': True})

def logout_view(request):
    return render(request, 'logout.html', {'exclude_header_footer': True})
