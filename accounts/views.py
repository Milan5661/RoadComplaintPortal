from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordChangeForm
from django.urls import reverse
from .models import CustomUser  # Assuming you have a custom user model for security questions.

User = get_user_model()

# Register view
def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password1 = request.POST["password1"]
        password2 = request.POST["password2"]
        security_answer_1 = request.POST["security_answer_1"]
        security_answer_2 = request.POST["security_answer_2"]

        if password1 == password2:
            if User.objects.filter(username=username).exists():
                messages.error(request, "Username already taken.")
            elif User.objects.filter(email=email).exists():
                messages.error(request, "Email already registered.")
            else:
                user = User.objects.create_user(username=username, email=email, password=password1)
                user.security_answer_1 = security_answer_1
                user.security_answer_2 = security_answer_2
                user.save()
                messages.success(request, "Account created successfully. You can now log in.")
                return redirect("login")
        else:
            messages.error(request, "Passwords do not match.")
    return render(request, "register.html")

# Custom login view with failed attempt tracking
def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            user = None

        if user:
            if user.failed_login_attempts >= 5:
                # Redirect to security questions after 5 failed attempts
                return redirect(reverse('admin_password_reset') + f'?username={username}')

            user_auth = authenticate(request, username=username, password=password)
            if user_auth is not None:
                login(request, user_auth)
                user.failed_login_attempts = 0  # Reset failed attempts after successful login
                user.save()
                messages.success(request, "Login successful!")
                return redirect("dashboard")  # Update to your dashboard page
            else:
                user.failed_login_attempts += 1
                user.save()
                remaining_attempts = 5 - user.failed_login_attempts
                if remaining_attempts > 0:
                    messages.error(request, f"⚠️ Incorrect password! {remaining_attempts} attempts left before security check.")
                else:
                    messages.error(request, "🚨 Too many wrong attempts! Answer security questions to reset your password.")
        else:
            messages.error(request, "❌ User not found.")

    return render(request, "login.html")

# Logout view
def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("login")

# Password reset view (after security questions)
def reset_password(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        form = PasswordChangeForm(user, request.POST)
        if form.is_valid():
            user.set_password(form.cleaned_data['new_password1'])
            user.save()
            messages.success(request, "✅ Your password has been successfully reset! Please log in.")
            return redirect('login')
    else:
        form = PasswordChangeForm(user)

    return render(request, 'admin/password_reset.html', {'form': form})

# Security questions view
def security_questions_view(request):
    username = request.GET.get('username')

    if not username:
        return redirect('login')

    user = get_object_or_404(User, username=username)

    if request.method == 'POST':
        answer1 = request.POST.get('answer1')
        answer2 = request.POST.get('answer2')

        # Validate security answers
        if (user.security_answer_1.lower() == answer1.lower() and
            user.security_answer_2.lower() == answer2.lower()):
            # Correct answers, reset the failed login attempts
            user.failed_login_attempts = 0
            user.save()
            messages.success(request, "✅ Correct answers! Now reset your password.")
            return redirect(reverse('reset_password', args=[user.id]))
        else:
            messages.error(request, "🚫 Incorrect answers. Try again.")

    context = {'user': user}
    return render(request, "security_questions.html", context)
