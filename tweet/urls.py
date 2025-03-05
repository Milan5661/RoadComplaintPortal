from django.urls import path
from . import views
from .views import register_view, login_view, logout_view, index, submit_complaint, ComplaintListCreateView, complaint_form, complaints_list
from .views import dashboard
from .views import complaint_form
from .views import get_complaints
from django.contrib.auth.views import LogoutView

app_name="tweet"

urlpatterns = [
    path('', views.home, name='home'),
    path('submit-complaint/', complaint_form, name='complaint_form'),
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('complaints/', complaints_list, name='complaints-list'),
    path("dashboard/", dashboard, name="dashboard"),
    path("complaint-form/", complaint_form, name="complaint_form"),  
    path('api/complaints/', ComplaintListCreateView.as_view(), name='complaints-api'),
    path("api/complaints/", get_complaints, name="get_complaints"),
     path('logout/', LogoutView.as_view(next_page='home'), name='logout'),
]
