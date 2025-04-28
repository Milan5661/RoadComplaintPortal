from django.urls import path
from . import views
<<<<<<< HEAD
from .views import (
    register, login_view, logout_view, 
    complaint_form, complaints_list, my_complaints,
    ComplaintListCreateView, get_complaints, home,complaint_status,
)
=======
from .views import register_view, login_view, logout_view, index, submit_complaint, ComplaintListCreateView, complaint_form, complaints_list
from .views import complaint_form
from .views import get_complaints
from django.contrib.auth.views import LogoutView
>>>>>>> f599c6034d52f10e6f476523bdca757424f8e4a4

app_name = "tweet"

urlpatterns = [
    # Home Page
    path('', home, name='home'),

    # Admin Security Questions & Password Reset
    path('admin/set-security-questions/', views.set_admin_security_questions, name='set_admin_security_questions'),
    path('admin/password-reset/', views.admin_password_reset, name='admin_password_reset'),

    # User Registration & Authentication
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
<<<<<<< HEAD

    # Complaint-related Views
    path('submit-complaint/', complaint_form, name='complaint_form'),
    path('complaints/', complaints_list, name='complaints_list'),  # fixed to complaints_list
    path('my-complaints/', my_complaints, name='my_complaints'),
    path('complaint-status/', complaint_status, name='complaint_status'),
     path('dashboard/', views.dashboard, name='dashboard'),

    # API Endpoints
    path('api/complaints/json/', get_complaints, name='get_complaints'),  # JSON for map or frontend
    path('api/complaints/', ComplaintListCreateView.as_view(), name='complaints_api'),  # DRF API for complaints
=======
    path('complaints/', complaints_list, name='complaints-list'),
    path("complaint-form/", complaint_form, name="complaint_form"),  
    path('api/complaints/', ComplaintListCreateView.as_view(), name='complaints-api'),
    path("api/complaints/", get_complaints, name="get_complaints"),
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),
>>>>>>> f599c6034d52f10e6f476523bdca757424f8e4a4
]
