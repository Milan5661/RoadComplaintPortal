import re
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordChangeForm
from django.urls import reverse
from accounts.forms import UserRegistrationForm, AdminSecurityQuestionForm, AdminPasswordResetForm
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

            # Create the user as inactive
            user = User.objects.create_user(username=username, email=email, password=password, is_active=False)
            user.security_question_1 = "What is your favourite food?"
            user.security_answer_1 = form.cleaned_data["security_answer_1"]
            user.security_question_2 = "What is your pet name?"
            user.security_answer_2 = form.cleaned_data["security_answer_2"]
            user.save()

            # Send activation email
            current_site = get_current_site(request)
            subject = 'Activate Your Road Complaint Portal Account'
            message = render_to_string('accounts/activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            send_mail(subject, message, None, [user.email], fail_silently=False)
            messages.success(request, "Account created! Please check your email to activate your account.")
            return redirect("login")
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

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            user = None

        if user:
            if user.failed_login_attempts >= 5:
                # Redirect to appropriate security questions page after 5 failed attempts
                if user.is_superuser:
                    return redirect(reverse('admin_password_reset') + f'?username={username}')
                else:
                    return redirect(reverse('security_questions') + f'?username={username}')

            user_auth = authenticate(request, username=username, password=password)
            if user_auth is not None:
                login(request, user_auth)
                user.failed_login_attempts = 0  # Reset failed attempts after successful login
                user.save()
                messages.success(request, "Login successful!")
                return redirect("home")  # Redirect to home page after login
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
def reset_password(request):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    user_id = request.session.get('reset_user_id')
    if not user_id:
        return redirect('security_questions')
    user = get_object_or_404(User, id=user_id)
    if request.method == "POST":
        new_password = request.POST.get("new_password")
        if new_password:
            user.set_password(new_password)
            user.save()
            messages.success(request, "Password updated successfully!")
            request.session.pop('reset_user_id', None)
            return redirect("login")
        else:
            messages.error(request, "Password cannot be empty.")
    return render(request, "reset_password.html")

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

