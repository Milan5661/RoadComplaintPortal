import re
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordChangeForm
from django.urls import reverse
from accounts.forms import UserRegistrationForm, AdminSecurityQuestionForm, AdminPasswordResetForm, AdminRegistrationForm
from .models import CustomUser  # Assuming you have a custom user model for security questions.
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.tokens import default_token_generator
from django.http import HttpResponse

User = get_user_model()

# Register view
def register(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]

            if User.objects.filter(username=username).exists():
                form.add_error("username", "Username already taken.")
                return render(request, "register.html", {"form": form})

            if User.objects.filter(email=email).exists():
                form.add_error("email", "Email already registered.")
                return render(request, "register.html", {"form": form})

            try:
                # Create the user as active (no email verification needed)
                user = User.objects.create_user(username=username, email=email, password=password, is_active=True)
                user.security_question_1 = "What is your favourite food?"
                user.security_answer_1 = form.cleaned_data["security_answer_1"]
                user.security_question_2 = "What is your childhood name?"
                user.security_answer_2 = form.cleaned_data["security_answer_2"]
                user.save()

                messages.success(request, "Account created successfully! You can now log in.")
                return redirect("login")
                    
            except Exception as e:
                messages.error(request, f"Failed to create account. Please try again. Error: {str(e)}")
                return render(request, "register.html", {"form": form})
        else:
            return render(request, "register.html", {"form": form})
    else:
        form = UserRegistrationForm()
    return render(request, "register.html", {"form": form})

# Custom login view with failed attempt tracking
def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user_type = request.POST.get("user_type", "user")

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            messages.error(request, "❌ User not found.")
            return render(request, "login.html")

        if user.failed_login_attempts >= 5:
            # Redirect to appropriate security questions page after 5 failed attempts
            if user.is_superuser:
                return redirect(reverse('admin_password_reset') + f'?username={username}')
            else:
                return redirect(reverse('security_questions') + f'?username={username}')

        user_auth = authenticate(request, username=username, password=password)
        if user_auth is not None:
            # Check if user type matches
            if user_type == "admin" and not user_auth.is_superuser:
                messages.error(request, "❌ This account is not an admin account.")
                return render(request, "login.html")
            elif user_type == "user" and user_auth.is_superuser:
                messages.error(request, "❌ Please use admin login for admin accounts.")
                return render(request, "login.html")

            login(request, user_auth)
            user.failed_login_attempts = 0  # Reset failed attempts after successful login
            user.save()
            messages.success(request, "Login successful!")
            # REDIRECT BASED ON USER TYPE
            if user_type == "admin":
                return redirect("/admin/")  # Redirect to Django admin panel
            else:
                return redirect("home")  # homepage for regular users
        else:
            user.failed_login_attempts += 1
            user.save()
            remaining_attempts = 5 - user.failed_login_attempts
            if remaining_attempts > 0:
                messages.error(request, f"⚠️ Incorrect password! {remaining_attempts} attempts left before security check.")
            else:
                messages.error(request, "🚨 Too many wrong attempts! Answer security questions to reset your password.")

    return render(request, "login.html")

# Logout view
def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("login")

# Password reset view (after security questions)
from .forms import UserPasswordResetForm

def reset_password(request):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    user_id = request.session.get('reset_user_id')
    if not user_id:
        return redirect('security_questions')
    user = get_object_or_404(User, id=user_id)
    form = UserPasswordResetForm()
    if request.method == "POST":
        form = UserPasswordResetForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data["new_password"]
            user.set_password(new_password)
            user.save()
            messages.success(request, "Password updated successfully!")
            request.session.pop('reset_user_id', None)
            return redirect("login")
        else:
            messages.error(request, "Please correct the errors below.")
    return render(request, "reset_password.html", {"form": form})

# Security questions view
from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse

def security_questions_view(request):
    User = get_user_model()
    user_obj = None
    username = ""
    if request.method == "POST":
        username = request.POST.get("username")
        answer1 = request.POST.get("answer1")
        answer2 = request.POST.get("answer2")
        try:
            user_obj = User.objects.get(username=username)
            if (
                user_obj.security_answer_1 and user_obj.security_answer_2 and
                user_obj.security_answer_1.strip().lower() == answer1.strip().lower() and
                user_obj.security_answer_2.strip().lower() == answer2.strip().lower()
            ):
                request.session['reset_user_id'] = user_obj.id
                messages.success(request, "✅ Correct answers! Now reset your password.")
                return redirect(reverse('reset_password'))
            else:
                messages.error(request, "🚫 Incorrect answers. Try again.")
        except User.DoesNotExist:
            messages.error(request, "❌ User not found.")
    elif request.method == "GET" and request.GET.get("username"):
        username = request.GET.get("username")
        try:
            user_obj = User.objects.get(username=username)
        except User.DoesNotExist:
            user_obj = None
    return render(request, "security_questions.html", {"user_obj": user_obj, "username": username})

def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Your account has been activated! You can now log in.')
        return redirect('login')
    else:
        return HttpResponse('Activation link is invalid!')

def about(request):
    pass  # This view is now removed

def admin_register(request):
    if request.method == "POST":
        form = AdminRegistrationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]

            if User.objects.filter(username=username).exists():
                form.add_error("username", "Username already taken.")
                return render(request, "admin_register.html", {"form": form})

            if User.objects.filter(email=email).exists():
                form.add_error("email", "Email already registered.")
                return render(request, "admin_register.html", {"form": form})

            try:
                # Create the user as superuser
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    is_active=True,
                    is_staff=True,
                    is_superuser=True
                )
                
                # Create AdminProfile and set security answers
                from tweet.models import AdminProfile
                profile = AdminProfile.objects.create(user=user)
                profile.set_security_answers(
                    form.cleaned_data["security_answer_1"],
                    form.cleaned_data["security_answer_2"]
                )

                messages.success(request, "Admin account created successfully! You can now log in.")
                return redirect("login")
                    
            except Exception as e:
                messages.error(request, f"Failed to create admin account. Please try again. Error: {str(e)}")
                return render(request, "admin_register.html", {"form": form})
        else:
            # If form is invalid, show the errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
            return render(request, "admin_register.html", {"form": form})
    else:
        form = AdminRegistrationForm()
    return render(request, "admin_register.html", {"form": form})

