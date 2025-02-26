from django.urls import path
from . import views
from .views import register_view, login_view, logout_view, index, submit_complaint, ComplaintListCreateView, complaint_form

urlpatterns = [
    path('complaints/', views.complaints_list, name='complaints_list'),
    path('submit/', views.submit_complaint, name='submit_complaint'),
    path('', index, name='home'),
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('complaints/', ComplaintListCreateView.as_view(), name='complaints_list'),
    path('submit/', submit_complaint, name='submit_complaint'),
    path('add-complaint/', complaint_form, name='complaint_form'),
]
