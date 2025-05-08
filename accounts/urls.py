from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    path('security-questions/', views.security_questions_view, name='security_questions'),
    path('reset-password/', views.reset_password, name='reset_password'),
]
