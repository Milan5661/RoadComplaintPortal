from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.http import JsonResponse
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from rest_framework import generics
from .forms import UserRegistrationForm, ComplaintForm, AdminSecurityQuestionForm, AdminPasswordResetForm
from .models import Complaint, AdminProfile
from .serializers import ComplaintSerializer
import random
import re
from django.core.paginator import Paginator
# ----------------- Static Pages -----------------

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password

User = get_user_model()


def set_admin_security_questions(request):
    if not request.user.is_superuser:
        messages.error(request, "Only admin can set security questions.")
        return redirect('dashboard')
    try:
        profile = AdminProfile.objects.get(user=request.user)
    except AdminProfile.DoesNotExist:
        profile = AdminProfile(user=request.user)
    if request.method == 'POST':
        form = AdminSecurityQuestionForm(request.POST)
        if form.is_valid():
            profile.set_security_answers(form.cleaned_data['answer1'], form.cleaned_data['answer2'])
            messages.success(request, "Security questions updated successfully.")
            return redirect('dashboard')
    else:
        form = AdminSecurityQuestionForm()
    return render(request, 'set_admin_security_questions.html', {'form': form})


def admin_password_reset(request):
    if request.method == 'POST':
        form = AdminPasswordResetForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            answer1 = form.cleaned_data['answer1']
            answer2 = form.cleaned_data['answer2']
            new_password = form.cleaned_data['new_password']
            try:
                user = User.objects.get(username=username, is_superuser=True)
                profile = AdminProfile.objects.get(user=user)
            except (User.DoesNotExist, AdminProfile.DoesNotExist):
                messages.error(request, "Admin user or security questions not found.")
                return render(request, 'admin_password_reset.html', {'form': form})
            if profile.check_security_answers(answer1, answer2):
                user.set_password(new_password)
                user.save()
                messages.success(request, "Password reset successful. You can now log in with your new password.")
                return redirect('login')
            else:
                messages.error(request, "Security answers incorrect. Please try again or contact support.")
    else:
        form = AdminPasswordResetForm()
    return render(request, 'admin_password_reset.html', {'form': form})

def home(request):
    return render(request, "home.html")

<<<<<<< HEAD
=======
# Home Page
>>>>>>> f599c6034d52f10e6f476523bdca757424f8e4a4
def index(request):
    return render(request, 'base.html')

# ----------------- User Authentication -----------------

<<<<<<< HEAD
=======
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

# View Complaints
def complaints_list(request):
    complaints = Complaint.objects.all().order_by('-date_reported')
    return render(request, "complaints_list.html", {"complaints": complaints})

# User Authentication Views
>>>>>>> f599c6034d52f10e6f476523bdca757424f8e4a4
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

<<<<<<< HEAD
def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            # Validate email domain
            if not re.match(r'^[a-zA-Z0-9_.+-]+@gmail\.com$', email):
                messages.error(request, 'Please enter a valid Gmail address.')
                return redirect('register')
    else:
        form = UserRegistrationForm()
    return render(request, 'register.html', {'form': form})

# ----------------- Complaint Related -----------------

@login_required
def submit_complaint(request):
    if request.method == "POST":
        description = request.POST.get("description")
        image = request.FILES.get("image")
        address = request.POST.get("address")
        latitude = request.POST.get("latitude")
        longitude = request.POST.get("longitude")

        if not description or not image:
            return render(request, "complaint_form.html", {"error": "All fields are required."})

        complaint = Complaint(
            user=request.user,
            description=description,
            image=image,
            address=address,
            latitude=latitude,
            longitude=longitude
        )
        complaint.save()

        return redirect('my_complaints')

    return render(request, "complaint_form.html")

@login_required
def complaint_form(request):
    form = ComplaintForm()
    if request.method == "POST":
        form = ComplaintForm(request.POST, request.FILES)
        if form.is_valid():
            complaint = form.save(commit=False)
            complaint.user = request.user
            complaint.save()

            # Send email
            
        else:
            messages.error(request, "Error submitting complaint. Please try again.")
    return render(request, "complaint_form.html", {"form": form})

@login_required
def my_complaints(request):
    complaints_list = Complaint.objects.filter(user=request.user).order_by('-created_at')
    paginator = Paginator(complaints_list, 6)  # Show 6 complaints per page

    page_number = request.GET.get('page')
    complaints = paginator.get_page(page_number)

    return render(request, 'my_complaints.html', {'complaints': complaints})


def complaint_status(request):
    # Fetch complaints that belong to the logged-in user
    complaints = Complaint.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'complaint_status.html', {'complaints': complaints})


def complaints_list(request):
    complaints = Complaint.objects.all().order_by('-created_at')
    return render(request, "complaints_list.html", {"complaints": complaints})

# ----------------- API (DRF) -----------------

class ComplaintListCreateView(generics.ListCreateAPIView):
    queryset = Complaint.objects.all().order_by('-created_at')
    serializer_class = ComplaintSerializer

# ----------------- Maps Data -----------------
=======
def home(request):
    # Get complaint statistics for the counters
    total_complaints = Complaint.objects.count()
    pending_complaints = Complaint.objects.filter(status="Pending").count()
    in_progress_complaints = Complaint.objects.filter(status="In Progress").count()
    resolved_complaints = Complaint.objects.filter(status="Resolved").count()
    
    context = {
        "total_complaints": total_complaints,
        "pending_complaints": pending_complaints,
        "in_progress_complaints": in_progress_complaints,
        "resolved_complaints": resolved_complaints
    }
    
    return render(request, "home.html", context)
>>>>>>> f599c6034d52f10e6f476523bdca757424f8e4a4

def get_complaints(request):
    complaints = list(Complaint.objects.values("latitude", "longitude", "description"))
    return JsonResponse(complaints, safe=False)

<<<<<<< HEAD
def dashboard(request):
    total_complaints = Complaint.objects.count()
    resolved_complaints = Complaint.objects.filter(status='Resolved').count()
    pending_complaints = Complaint.objects.filter(status='Pending').count()

    context = {
        'total_complaints': total_complaints,
        'resolved_complaints': resolved_complaints,
        'pending_complaints': pending_complaints,
    }
    return render(request, 'dashboard.html', context)
=======
class ComplaintListCreateView(generics.ListCreateAPIView):
    queryset = Complaint.objects.all().order_by('-date_reported')
    serializer_class = ComplaintSerializer

# Hide header/footer for login, register, and logout pages
def login_view(request):
    return render(request, 'login.html', {'exclude_header_footer': True})

def register_view(request):
    return render(request, 'register.html', {'exclude_header_footer': True})

def logout_view(request):
    return render(request, 'logout.html', {'exclude_header_footer': True})
>>>>>>> f599c6034d52f10e6f476523bdca757424f8e4a4
