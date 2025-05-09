from django.urls import path
from . import views

from .views import (
    register, login_view, logout_view, 
    complaint_form, complaints_list, my_complaints,
    ComplaintListCreateView, get_complaints, home,complaint_status,
)

app_name = "tweet"

urlpatterns = [
    path('report/', views.admin_report, name='admin_report'),
    path('report-generation/', views.report_generation, name='report_generation'),
    # Home Page
    path('', home, name='home'),

    # Admin Security Questions & Password Reset
    path('admin/set-security-questions/', views.set_admin_security_questions, name='set_admin_security_questions'),
    path('password-reset/', views.password_reset, name='password_reset'),

    # User Registration & Authentication
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),

    # Complaint-related Views
    path('submit-complaint/', complaint_form, name='complaint_form'),
    path('complaints/', complaints_list, name='complaints_list'),  # fixed to complaints_list
    path('my-complaints/', my_complaints, name='my_complaints'),
    path('complaint-status/', complaint_status, name='complaint_status'),


    # API Endpoints
    path('api/complaints/json/', get_complaints, name='get_complaints'),  # JSON for map or frontend
    path('api/complaints/', ComplaintListCreateView.as_view(), name='complaints_api'),  # DRF API for complaints

]
