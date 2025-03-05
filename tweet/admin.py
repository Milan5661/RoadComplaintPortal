from django.contrib import admin
from .models import Complaint



class ComplaintAdmin(admin.ModelAdmin):
    list_display = ("user", "description", "status", "date_reported","address")
    list_filter = ("status",)
    search_fields = ("user__username", "description")

admin.site.register(Complaint, ComplaintAdmin)