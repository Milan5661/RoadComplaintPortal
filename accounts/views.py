from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password1 = request.POST["password1"]
        password2 = request.POST["password2"]

        if password1 == password2:
            if User.objects.filter(username=username).exists():
                messages.error(request, "Username already taken.")
            elif User.objects.filter(email=email).exists():
                messages.error(request, "Email already registered.")
            else:
                user = User.objects.create_user(username=username, email=email, password=password1)
                user.save()
                messages.success(request, "Account created successfully. You can now log in.")
                return redirect("login")
        else:
            messages.error(request, "Passwords do not match.")
    return render(request, "register.html")

def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "Login successful!")
            return redirect("dashboard")  # Change to your dashboard URL
        else:
            messages.error(request, "Invalid credentials.")
    
    return render(request, "login.html")

def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("login")
def home(request):
    return render(request, "home.html")

from django.shortcuts import render

def dashboard(request):
    return render(request, "dashboard.html")

def user_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("home")  # Redirect to home or dashboard after login
        else:
            messages.error(request, "Incorrect username or password.")  # Error message

    return render(request, "login.html") 

