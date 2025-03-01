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


urlpatterns = [
    path('admin/', admin.site.urls),  # Add this line
    path('', accounts_views.home, name='home'),
    path('complaint-form/', tweet_views.complaint_form, name='complaint_form'),
    path('submit-complaint/', tweet_views.submit_complaint, name='submit_complaint'),
    path('complaints-list/', tweet_views.complaints_list, name='complaints_list'),
    path('register/', accounts_views.register, name='register'),
    path('login/', accounts_views.login_view, name='login'),
    path('logout/', accounts_views.logout_view, name='logout'),
    path('complaints/', tweet_views.complaints, name='complaints'),
    path("tweet/", include("tweet.urls")),
    path("dashboard/", dashboard, name="dashboard"), 
    path("home/", home, name="home"),
    path("login/", user_login, name="login"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
