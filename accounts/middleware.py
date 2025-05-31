from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.core.cache import cache
from django.conf import settings
import hashlib

class SessionIsolationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            # Get the current path
            current_path = request.path_info
            
            # Check if user is trying to access admin panel
            is_admin_path = current_path.startswith('/admin/')
            
            # Get browser tab identifier from request
            tab_id = request.COOKIES.get('tab_id')
            if not tab_id and request.session.session_key:
                # Generate a new tab ID if none exists
                tab_id = hashlib.md5(str(request.session.session_key).encode()).hexdigest()
                request.COOKIES['tab_id'] = tab_id
            
            # If no session key or tab_id, force logout
            if not request.session.session_key or not tab_id:
                self._force_logout(request, tab_id)
                return redirect('login')
            
            # Get user type and session info from cache
            user_type = cache.get(f'user_type_{request.user.id}_{tab_id}')
            session_key = cache.get(f'session_key_{request.user.id}_{tab_id}')
            
            # If no user type in cache for this tab, force logout
            if not user_type or not session_key:
                self._force_logout(request, tab_id)
                return redirect('login')
            
            # Validate session
            if session_key != request.session.session_key:
                self._force_logout(request, tab_id)
                return redirect('login')
            
            # Strict path access control
            if is_admin_path:
                if user_type != 'admin' or not request.user.is_superuser:
                    messages.error(request, "Access denied. Admin login required.")
                    self._force_logout(request, tab_id)
                    return redirect('login')
            else:
                if user_type == 'admin':
                    messages.error(request, "Please use admin panel for admin access.")
                    self._force_logout(request, tab_id)
                    return redirect('login')

        response = self.get_response(request)
        
        # Set tab_id cookie if not exists and we have a session
        if not request.COOKIES.get('tab_id') and request.session.session_key:
            tab_id = hashlib.md5(str(request.session.session_key).encode()).hexdigest()
            response.set_cookie('tab_id', tab_id, max_age=3600, httponly=True, samesite='Lax')
            
        return response

    def _force_logout(self, request, tab_id):
        """Helper method to force logout and clear all session data"""
        if request.user.is_authenticated:
            # Clear cache for this tab
            if tab_id:
                cache.delete(f'user_type_{request.user.id}_{tab_id}')
                cache.delete(f'session_key_{request.user.id}_{tab_id}')
            
            # Clear session
            request.session.flush()
            
            # Logout
            logout(request)
            
            messages.error(request, "Session expired. Please login again.") 