from django.urls import path
from . import views

urlpatterns = [
    path('complaints/', views.complaints_list, name='complaints_list'),
    path('submit/', views.submit_complaint, name='submit_complaint'),
]
