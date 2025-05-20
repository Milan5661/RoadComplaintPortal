# ... existing code ...

# Email Configuration
# For development (prints emails to console)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# For production (Gmail SMTP) - Commented out for development
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_USE_SSL = False
# EMAIL_HOST_USER = 'your-email@gmail.com'
# EMAIL_HOST_PASSWORD = 'your-app-password'
# DEFAULT_FROM_EMAIL = 'your-email@gmail.com'
# SERVER_EMAIL = 'your-email@gmail.com'

# Email timeout settings
EMAIL_TIMEOUT = 60  # Increased timeout to 60 seconds

# Debug settings for development
DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Backup current Jazzmin settings if present
JAZZMIN_SETTINGS_BACKUP = globals().get('JAZZMIN_SETTINGS', None)

JAZZMIN_SETTINGS = {
    # Branding
    "site_title": "RoadComplaintPortal",
    "site_header": "RoadComplaintPortal",
    "site_brand": "Road Complaint Portal",
    "welcome_sign": "Welcome to Road Complaint Portal Admin",
    "copyright": "RoadComplaintPortal © 2025",

    # Logo removed for now
    # "site_logo": "img/logo.png",
    # "site_logo_classes": "img-circle",

    # Top menu links
    "topmenu_links": [
        {"name": "Home", "url": "/", "new_window": True},
        {"model": "auth.User"},
        {"app": "tweet"},
        {"name": "Support", "url": "https://support.example.com", "new_window": True},
    ],

    # User menu links
    "usermenu_links": [
        {"name": "Support", "url": "https://support.example.com", "new_window": True},
    ],

    # Side menu customization
    "show_sidebar": True,
    "navigation_expanded": True,
    "hide_apps": [],
    "hide_models": [],
    "order_with_respect_to": ["auth", "tweet", "accounts"],

    # Custom icons for apps/models
    "icons": {
        "auth": "fas fa-users-cog",
        "tweet.complaint": "fas fa-road",
        "accounts.customuser": "fas fa-user-shield",
    },

    # Change the default theme (Bootswatch themes)
    "theme": "darkly",  # Changed to a dark theme

    # Custom CSS/JS
    # "custom_css": "css/custom_admin.css",
    # "custom_js": "js/custom_admin.js",

    # Misc
    "show_ui_builder": True,  # Show the UI builder in the admin
    "changeform_format": "horizontal_tabs",  # "single", "horizontal_tabs", "collapsible", "vertical_tabs"
    "language_chooser": True,  # Show language chooser in the user menu
}

# ... existing code ... 