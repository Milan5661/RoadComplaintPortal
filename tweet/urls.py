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

    # Preview User Management Dashboard
    path('preview/', views.user_management_preview, name='user_management_preview'),

    # User Management Views
    path('admin/users/', views.user_management, name='user_management'),
    path('admin/users/<int:user_id>/toggle-status/', views.toggle_user_status, name='toggle_user_status'),
    path('admin/users/<int:user_id>/reset-password/', views.reset_user_password, name='reset_user_password'),

    # New admin login view
    path('admin-login/', views.admin_login, name='admin_login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('users/', views.user_management, name='user_management'),
    # path('complaints/', views.complaint_management, name='complaint_management'),
    # path('reports/', views.reports, name='reports'),
    # path('settings/', views.settings, name='settings'),

    # Notification URLs
    path('notifications/mark-read/<int:notification_id>/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/mark-all-read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
    path('complaints/<int:complaint_id>/update-status/', views.update_complaint_status, name='update_complaint_status'),
    path('notifications/api/', views.notifications_api, name='notifications_api'),
]
