from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
import datetime
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.http import JsonResponse
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from rest_framework import generics
from accounts.forms import UserRegistrationForm, ComplaintForm, AdminSecurityQuestionForm, AdminPasswordResetForm
from .models import Complaint, AdminProfile
from .serializers import ComplaintSerializer
import random
import re
from django.core.paginator import Paginator
# ----------------- Static Pages -------------

@staff_member_required
def report_generation(request):
    qs = Complaint.objects.all()
    status = request.GET.get('status')
    period = request.GET.get('period', 'all')
    from_date = request.GET.get('from_date')
    to_date = request.GET.get('to_date')
    if status:
        qs = qs.filter(status=status)
    if period == 'today':
        today = timezone.now().date()
        qs = qs.filter(created_at__date=today)
    elif period == 'week':
        today = timezone.now().date()
        start_week = today - datetime.timedelta(days=today.weekday())
        qs = qs.filter(created_at__date__gte=start_week)
    elif period == 'month':
        now = timezone.now()
        qs = qs.filter(created_at__year=now.year, created_at__month=now.month)
    elif period == 'custom' and from_date and to_date:
        qs = qs.filter(created_at__date__gte=from_date, created_at__date__lte=to_date)
    return render(request, 'report_generation.html', {'complaints': qs, 'request': request})

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


from accounts.forms import UserPasswordResetForm
from accounts.models import CustomUser

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


from django import forms

def password_reset(request):
    from django import forms
    class UnifiedPasswordResetForm(forms.Form):
        username = forms.CharField(label="Username", max_length=150)
        new_password = forms.CharField(label="New Password", widget=forms.PasswordInput, min_length=6, required=False)
        confirm_password = forms.CharField(label="Confirm Password", widget=forms.PasswordInput, min_length=6, required=False)
        # Security answers handled in template
        def clean(self):
            cleaned_data = super().clean()
            pw = cleaned_data.get('new_password')
            cpw = cleaned_data.get('confirm_password')
            if pw or cpw:
                if pw != cpw:
                    raise forms.ValidationError("Passwords do not match.")
            return cleaned_data

    show_questions = False
    show_password_fields = False
    question1 = ''
    question2 = ''
    user_obj = None
    username = ''

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        answer1 = request.POST.get('answer1', '').strip()
        answer2 = request.POST.get('answer2', '').strip()
        new_password = request.POST.get('new_password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()
        form = UnifiedPasswordResetForm(request.POST)

        # Always fetch user if username is provided
        if username:
            try:
                user_obj = CustomUser.objects.get(username=username)
                if user_obj.is_superuser:
                    question1 = "What is your favourite food?"
                    question2 = "What is your childhood name?"
                else:
                    question1 = "What is your favourite food?"
                    question2 = "What is your childhood name?"
                show_questions = True
            except CustomUser.DoesNotExist:
                messages.error(request, "User not found.")
                form = UnifiedPasswordResetForm()
                return render(request, 'password_reset.html', {
                    'form': form,
                    'show_questions': False,
                    'show_password_fields': False,
                    'question1': '',
                    'question2': '',
                    'username': username
                })

        # If answers provided, check them
        if username and answer1 and answer2 and not new_password and not confirm_password:
            if user_obj and user_obj.security_answer_1 and user_obj.security_answer_2 and \
               user_obj.security_answer_1.strip().lower() == answer1.lower() and \
               user_obj.security_answer_2.strip().lower() == answer2.lower():
                show_password_fields = True
            else:
                messages.error(request, "Security answer didn't match.")
                show_password_fields = False

        # If answers and new passwords provided, check all
        elif username and answer1 and answer2 and new_password and confirm_password:
            if user_obj and user_obj.security_answer_1 and user_obj.security_answer_2 and \
               user_obj.security_answer_1.strip().lower() == answer1.lower() and \
               user_obj.security_answer_2.strip().lower() == answer2.lower():
                # Password validation (same as registration)
                errors = []
                if len(new_password) < 8 or len(new_password) > 15:
                    errors.append("Password must be between 8 and 15 characters long.")
                if not any(c.isupper() for c in new_password):
                    errors.append("Password must contain at least one uppercase letter.")
                if not any(c.islower() for c in new_password):
                    errors.append("Password must contain at least one lowercase letter.")
                if not any(c.isdigit() for c in new_password):
                    errors.append("Password must contain at least one number.")
                if errors:
                    for err in errors:
                        messages.error(request, err)
                    show_password_fields = True
                elif form.is_valid():
                    user_obj.set_password(new_password)
                    user_obj.save()
                    messages.success(request, "Password reset successful. You can now log in with your new password.")
                    return redirect('login')
                else:
                    show_password_fields = True
            else:
                messages.error(request, "Security answer didn't match.")
                show_password_fields = False

    else:
        form = UnifiedPasswordResetForm()

    context = {
        'form': form,
        'show_questions': show_questions,
        'show_password_fields': show_password_fields,
        'question1': question1,
        'question2': question2,
        'username': username
    }
    return render(request, 'password_reset.html', context)


from django.utils import timezone
from datetime import timedelta

def home(request):
    from django.db.models import Q
    # Get filter parameters from request
    filter_period = request.GET.get('filter', '7d')
    month = request.GET.get('month')
    year = request.GET.get('year')
    now = timezone.now()
    complaints_qs = Complaint.objects.filter(is_approved=True)

    # Default: last 7 days
    if filter_period == '7d' or not filter_period:
        start_date = now - timedelta(days=7)
        period_label = 'Last 7 Days'
        filtered_qs = complaints_qs.filter(created_at__gte=start_date)
    elif filter_period == 'month':
        start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        period_label = now.strftime('%B %Y')
        filtered_qs = complaints_qs.filter(created_at__gte=start_date)
    elif filter_period == 'year':
        start_date = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        period_label = now.strftime('%Y')
        filtered_qs = complaints_qs.filter(created_at__gte=start_date)
    elif filter_period == 'custom_month' and month:
        try:
            y, m = map(int, month.split('-'))
            start_date = now.replace(year=y, month=m, day=1, hour=0, minute=0, second=0, microsecond=0)
            if m == 12:
                end_date = now.replace(year=y+1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            else:
                end_date = now.replace(year=y, month=m+1, day=1, hour=0, minute=0, second=0, microsecond=0)
            period_label = start_date.strftime('%B %Y')
            filtered_qs = complaints_qs.filter(created_at__gte=start_date, created_at__lt=end_date)
        except Exception:
            filtered_qs = complaints_qs.none()
            period_label = 'Custom Month'
    elif filter_period == 'custom_year' and year:
        try:
            y = int(year)
            start_date = now.replace(year=y, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            end_date = now.replace(year=y+1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            period_label = str(y)
            filtered_qs = complaints_qs.filter(created_at__gte=start_date, created_at__lt=end_date)
        except Exception:
            filtered_qs = complaints_qs.none()
            period_label = 'Custom Year'
    else:
        filtered_qs = complaints_qs
        period_label = 'All Time'

    # Stats for filtered period
    complaints_period_total = filtered_qs.count()
    complaints_period_pending = filtered_qs.filter(status='Pending').count()
    complaints_period_in_progress = filtered_qs.filter(status='In Progress').count()
    complaints_period_resolved = filtered_qs.filter(status='Resolved').count()

    # All time stats (for pie chart)
    total_complaints = complaints_qs.count()
    resolved_complaints = complaints_qs.filter(status='Resolved').count()
    pending_complaints = complaints_qs.filter(status='Pending').count()
    in_progress_complaints = complaints_qs.filter(status='In Progress').count()
    recent_complaints = complaints_qs.order_by('-created_at')[:3]

    # All-time chart data (per year)
    years = complaints_qs.dates('created_at', 'year')
    year_labels = [str(y.year) for y in years]
    reported_per_year = [complaints_qs.filter(created_at__year=y.year).count() for y in years]
    fixed_per_year = [complaints_qs.filter(status='Resolved', created_at__year=y.year).count() for y in years]

    chart_labels = ['Resolved', 'Pending', 'In Progress']
    chart_data = [resolved_complaints, pending_complaints, in_progress_complaints]

    context = {
        'total_complaints': total_complaints,
        'resolved_complaints': resolved_complaints,
        'pending_complaints': pending_complaints,
        'in_progress_complaints': in_progress_complaints,
        'recent_complaints': recent_complaints,
        'chart_labels': chart_labels,
        'chart_data': chart_data,
        'complaints_last_7_days': complaints_period_total,
        'complaints_7d_pending': complaints_period_pending,
        'complaints_7d_in_progress': complaints_period_in_progress,
        'complaints_7d_resolved': complaints_period_resolved,
        'year_labels': year_labels,
        'reported_per_year': reported_per_year,
        'fixed_per_year': fixed_per_year,
        'filter': filter_period,
        'month': month,
        'year': year,
        'period_label': period_label,
    }
    return render(request, "home.html", context)



def index(request):
    return render(request, 'base.html')

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
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user_auth = authenticate(request, username=username, password=password)
        
        if user_auth is not None:
            login(request, user_auth)
            return redirect('home')  # or wherever you want
        else:
            messages.error(request, "Incorrect username or password. Please try again.")
            return redirect('login')
    
    return render(request, 'login.html')

@login_required
def logout_view(request):
    logout(request)
    return redirect('home')

from django.views.decorators.csrf import csrf_protect

@csrf_protect
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
        address = request.POST.get("address")
        latitude = request.POST.get("latitude")
        longitude = request.POST.get("longitude")

        # Ensure coordinates are present and valid
        error = None
        try:
            latitude = float(latitude)
            longitude = float(longitude)
        except (TypeError, ValueError):
            error = "Could not determine your location. Please use the 'Use My Current Location' button."

        if not description or error:
            return render(request, "complaint_form.html", {"error": error or "All fields are required."})

        complaint = Complaint(
            user=request.user,
            description=description,
            address=address,
            latitude=latitude,
            longitude=longitude
        )
        complaint.save()

        # Handle multiple images
        images = request.FILES.getlist('images')
        from .models import ComplaintImage
        for image in images:
            ComplaintImage.objects.create(complaint=complaint, image=image)

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

            # Save uploaded images to ComplaintImage
            images = request.FILES.getlist('images')
            from .models import ComplaintImage
            for image in images:
                ComplaintImage.objects.create(complaint=complaint, image=image)

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


@login_required
def complaints_list(request):
    from django.core.paginator import Paginator
    complaints_qs = Complaint.objects.filter(is_approved=True).order_by('-created_at')
    paginator = Paginator(complaints_qs, 7)  # 7 complaints per page
    page_number = request.GET.get('page')
    complaints = paginator.get_page(page_number)
    return render(request, "complaints_list.html", {"complaints": complaints})

# ----------------- API (DRF) -----------------

class ComplaintListCreateView(generics.ListCreateAPIView):
    queryset = Complaint.objects.all().order_by('-created_at')
    serializer_class = ComplaintSerializer

# ----------------- Maps Data -----------------

def get_complaints(request):
    complaints = list(Complaint.objects.values("latitude", "longitude", "description"))
    return JsonResponse(complaints, safe=False)

def dashboard(request):
    # Only count approved complaints
    total_complaints = Complaint.objects.filter(is_approved=True).count()
    resolved_complaints = Complaint.objects.filter(is_approved=True, status='Resolved').count()
    pending_complaints = Complaint.objects.filter(is_approved=True, status='Pending').count()

    context = {
        'total_complaints': total_complaints,
        'resolved_complaints': resolved_complaints,
        'pending_complaints': pending_complaints,
    }
    return render(request, 'dashboard.html', context)

