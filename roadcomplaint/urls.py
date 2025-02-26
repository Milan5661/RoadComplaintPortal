from django.contrib import admin
from django.urls import path,include
from tweet.views import index, ComplaintListCreateView, submit_complaint
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='home'),  # Home page route
    path('complaints/', ComplaintListCreateView.as_view(), name='complaints_list'),
    path('submit/', submit_complaint, name='submit_complaint'),
    path('admin/', admin.site.urls),
    path('', include('tweet.urls')), 
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
