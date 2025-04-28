from django.contrib import admin
from .models import Complaint
from django.utils.safestring import mark_safe

@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ('user', 'status', 'is_approved', 'created_at')  
    list_filter = ('status', 'is_approved', 'created_at')
    search_fields = ('description', 'address')
    date_hierarchy = 'created_at'  
    ordering = ('-created_at',)  
    list_per_page = 5
