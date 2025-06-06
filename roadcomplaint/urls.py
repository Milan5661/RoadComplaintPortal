from django.contrib import admin
from django.urls import path, include
from accounts import views as accounts_views
from tweet import views as tweet_views

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('accounts/', include('django.contrib.auth.urls')),  # Disabled default auth URLs to use custom password reset flow


    # Home page
    path('', tweet_views.home, name='home'),

    # Admin Security Questions & Password Reset at root (no /admin/ prefix to avoid conflict)
    path('admin-set-security-questions/', tweet_views.set_admin_security_questions, name='set_admin_security_questions'),
    path('admin-password-reset/', tweet_views.admin_password_reset, name='admin_password_reset'),
    path('admin-register/', accounts_views.admin_register, name='admin_register'),


    # Accounts-related
    path('register/', accounts_views.register, name='register'),
    path('login/', accounts_views.login_view, name='login'),
    path('logout/', accounts_views.logout_view, name='logout'),

    # Complaint-related
    path('submit-complaint/', tweet_views.complaint_form, name='submit_complaint'),
    path('complaints-list/', tweet_views.complaints_list, name='complaints_list'),
    path('complaints/', tweet_views.complaints_list, name='complaints'),

    # Tweet app
    path('tweet/', include(('tweet.urls', 'tweet'), namespace='tweet')),

    # Direct password reset route for accounts
    path('accounts/password_reset/', tweet_views.password_reset, name='accounts_password_reset'),
    path('accounts/', include('accounts.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
