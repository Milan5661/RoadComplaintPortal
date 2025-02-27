from django.shortcuts import render,redirect
from rest_framework import generics
from .models import Complaint
from .serializers import ComplaintSerializer
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required

def index(request):
    return render(request, 'index.html')

class ComplaintListCreateView(generics.ListCreateAPIView):
    serializer_class = ComplaintSerializer

    def get_queryset(self):
        return Complaint.objects.all().order_by('-date_reported')
def submit_complaint(request):
    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")
        image = request.FILES.get("image")
        latitude = request.POST.get("latitude")
        longitude = request.POST.get("longitude")

        if not title or not description or not latitude or not longitude:
            return JsonResponse({"error": "Missing required fields"}, status=400)

        complaint = Complaint.objects.create(
            title=title,
            description=description,
            image=image,
            latitude=latitude,
            longitude=longitude,
            user=request.user  # Assign the logged-in user
        )
        return JsonResponse({"message": "Complaint submitted successfully", "id": complaint.id})

    return JsonResponse({"error": "Invalid request method"}, status=405)


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
    complaints = Complaint.objects.all().values("id", "description", "image", "location", "date_reported")
    return JsonResponse({"complaints": list(complaints)})

# User Registration View
def register_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')  # Redirect to home after registration
    else:
        form = UserCreationForm()
    return render(request, 'tweet/register.html', {'form': form})

# User Login View
def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')  # Redirect after login
    else:
        form = AuthenticationForm()
    return render(request, 'tweet/login.html', {'form': form})

# User Logout View
@login_required
def logout_view(request):
    logout(request)
    return redirect('home')

def complaint_form(request):
    return render(request, 'complaint_form.html')