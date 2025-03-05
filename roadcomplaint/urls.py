from django.contrib import admin
from django.urls import path, include
from accounts import views as accounts_views
from tweet import views as tweet_views
from accounts.views import dashboard
from accounts.views import home
from django.conf import settings
from django.conf.urls.static import static
from tweet.views import home
from accounts.views import user_login
from django.contrib.auth import views as auth_views



urlpatterns = [
    path('admin/', admin.site.urls),  # Add this line
    path('', accounts_views.home, name='home'), 
    path('submit-complaint/', tweet_views.complaint_form, name='submit_complaint'),
    path('complaints-list/', tweet_views.complaints_list, name='complaints_list'),
    path('register/', accounts_views.register, name='register'),
    path('login/', accounts_views.login_view, name='login'),
    path('logout/', accounts_views.logout_view, name='logout'),
    path('complaints/', tweet_views.complaints_list, name='complaints-list'),
    path("tweet/", include("tweet.urls", namespace="tweet")),
    path("dashboard/", dashboard, name="dashboard"), 
    path("home/", home, name="home"),
    path("login/", user_login, name="login"),
    path("password-reset/", auth_views.PasswordResetView.as_view(), name="password_reset"),
    path("password-reset/done/", auth_views.PasswordResetDoneView.as_view(), name="password_reset_done"),
    path("password-reset-confirm/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path("password-reset-complete/", auth_views.PasswordResetCompleteView.as_view(), name="password_reset_complete"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
