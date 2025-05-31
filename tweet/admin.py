from django import forms
from django.contrib import admin
from django.urls import path
from django.shortcuts import render, redirect
from django.utils import timezone
from .models import Complaint, ComplaintImage, Notification
from django.utils.safestring import mark_safe
import datetime
from django.contrib import messages

admin.site.site_header = "Road Complaint Portal"
admin.site.site_title = "Road Complaint Portal"
admin.site.index_title = "Welcome to the Road Complaint Portal Admin"

class ComplaintAdminForm(forms.ModelForm):
    class Meta:
        model = Complaint
        exclude = ('rejection_reason',)
        widgets = {
            'estimated_completion': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def clean_estimated_completion(self):
        value = self.cleaned_data.get('estimated_completion')
        # Allow empty value
        return value

class ComplaintImageInline(admin.TabularInline):
    model = ComplaintImage
    extra = 0
    readonly_fields = ('image_tag',)

    def image_tag(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" style="max-height: 100px; max-width: 100px;" />')
        return "-"
    image_tag.short_description = 'Image Preview'

@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    form = ComplaintAdminForm
    inlines = [ComplaintImageInline]
    list_display = ('user', 'status', 'is_approved', 'created_at')  
    list_filter = ('status', 'is_approved', 'created_at')
    search_fields = ('description', 'address')
    date_hierarchy = 'created_at'  
    ordering = ('-created_at',)  
    list_per_page = 5
    list_editable = ('is_approved',)
    actions = ['approve_complaints', 'reject_complaints']
    readonly_fields = ('map_view',)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('report-generation/', self.admin_site.admin_view(self.report_generation_view), name='tweet_complaint_report_generation'),
            path('report-generation/pdf/', self.admin_site.admin_view(self.report_pdf_view), name='tweet_complaint_report_pdf'),
        ]
        return custom_urls + urls

    def delete_view(self, request, object_id, extra_context=None):
        obj = self.get_object(request, object_id)
        if request.method == "POST":
            reason = request.POST.get('deletion_reason', '')
            if obj and reason:
                try:
                    # Store complaint reference before deletion
                    complaint_ref = f"#{obj.id} ({obj.description[:30]}{'...' if len(obj.description) > 30 else ''})"
                    # Create notification before deletion
                    notification = Notification.objects.create(
                        user=obj.user,
                        complaint=obj,
                        complaint_reference=complaint_ref,
                        notification_type='deletion',
                        message=f"Your complaint {complaint_ref} has been deleted by admin. Reason: {reason}",
                        is_read=False
                    )
                    messages.success(request, f"Complaint deleted successfully. User has been notified with the reason.")
                except Exception as e:
                    messages.error(request, f"Error creating notification: {str(e)}")
        return super().delete_view(request, object_id, extra_context)

    def changelist_view(self, request, extra_context=None):
        if not extra_context:
            extra_context = {}
        extra_context['report_generation_url'] = '/admin/tweet/complaint/report-generation/'
        extra_context['show_report_generation_button'] = True
        # Add a custom button to the object-tools block (top right)
        if 'object_tools' not in extra_context:
            extra_context['object_tools'] = []
        extra_context['object_tools'].append({
            'url': extra_context['report_generation_url'],
            'label': 'Report Generation',
            'class': 'btn btn-info',
        })
        return super().changelist_view(request, extra_context=extra_context)

    def map_view(self, obj):
        if obj.latitude and obj.longitude:
            return mark_safe(f'''
                <iframe
                    width="400"
                    height="300"
                    frameborder="0"
                    style="border:0"
                    src="https://www.google.com/maps?q={obj.latitude},{obj.longitude}&hl=es;z=16&output=embed"
                    allowfullscreen>
                </iframe>
            ''')
        return "No location available"
    map_view.short_description = ""

    @admin.action(description='Approve selected complaints')
    def approve_complaints(self, request, queryset):
        queryset.update(is_approved=True)

    @admin.action(description='Reject selected complaints')
    def reject_complaints(self, request, queryset):
        queryset.update(is_approved=False)

    def save_model(self, request, obj, form, change):
        old_obj = None
        if obj.pk:
            old_obj = Complaint.objects.get(pk=obj.pk)
        super().save_model(request, obj, form, change)
        if old_obj:
            complaint_info = f"#{obj.id} ({obj.description[:30]}{'...' if len(obj.description) > 30 else ''})"
            # Status change
            if old_obj.status != obj.status:
                Notification.objects.create(
                    user=obj.user,
                    complaint=obj,
                    notification_type='status_change',
                    message=f"Complaint {complaint_info}: Status updated from {old_obj.status} to {obj.status}"
                )
            # Budget update
            if obj.budget_estimate and old_obj.budget_estimate != obj.budget_estimate:
                Notification.objects.create(
                    user=obj.user,
                    complaint=obj,
                    notification_type='budget_update',
                    message=f"Complaint {complaint_info}: Budget estimate: Rs {obj.budget_estimate}"
                )
            # Completion update
            if obj.estimated_completion and old_obj.estimated_completion != obj.estimated_completion:
                Notification.objects.create(
                    user=obj.user,
                    complaint=obj,
                    notification_type='completion_update',
                    message=f"Complaint {complaint_info}: Estimated completion date: {obj.estimated_completion.strftime('%Y-%m-%d')}"
                )

    def report_generation_view(self, request):
        # Filtering logic
        qs = Complaint.objects.all()
        status = request.GET.get('status')
        period = request.GET.get('period', 'all')
        from_date = request.GET.get('from_date')
        to_date = request.GET.get('to_date')

        if status:
            qs = qs.filter(status=status)
        if period == 'today':
            today = timezone.now().date()
            qs = qs.filter(created_at__date=today)
        elif period == 'week':
            today = timezone.now().date()
            start_week = today - datetime.timedelta(days=today.weekday())
            qs = qs.filter(created_at__date__gte=start_week)
        elif period == 'month':
            now = timezone.now()
            qs = qs.filter(created_at__year=now.year, created_at__month=now.month)
        elif period == 'custom' and from_date and to_date:
            qs = qs.filter(created_at__date__gte=from_date, created_at__date__lte=to_date)
        # Print mode (render printable template)
        if request.GET.get('print'):
            return render(request, 'admin_report_generation.html', {'complaints': qs, 'request': request, 'print_mode': True})
        # PDF download button
        pdf_url = request.get_full_path().replace('report-generation/', 'report-generation/pdf/')
        return render(request, 'admin_report_generation.html', {'complaints': qs, 'request': request, 'pdf_url': pdf_url})

    def report_pdf_view(self, request):
        from django.template.loader import get_template
        from django.http import HttpResponse
        from weasyprint import HTML
        qs = Complaint.objects.all()
        status = request.GET.get('status')
        period = request.GET.get('period', 'all')
        from_date = request.GET.get('from_date')
        to_date = request.GET.get('to_date')
        if status:
            qs = qs.filter(status=status)
        if period == 'today':
            today = timezone.now().date()
            qs = qs.filter(created_at__date=today)
        elif period == 'week':
            today = timezone.now().date()
            start_week = today - datetime.timedelta(days=today.weekday())
            qs = qs.filter(created_at__date__gte=start_week)
        elif period == 'month':
            now = timezone.now()
            qs = qs.filter(created_at__year=now.year, created_at__month=now.month)
        elif period == 'custom' and from_date and to_date:
            qs = qs.filter(created_at__date__gte=from_date, created_at__date__lte=to_date)
        pending_count = qs.filter(status='Pending').count()
        in_progress_count = qs.filter(status='In Progress').count()
        resolved_count = qs.filter(status='Resolved').count()
        template = get_template('pdf_report.html')
        html_string = template.render({
            'complaints': qs,
            'request': request,
            'pdf_mode': True,
            'pending_count': pending_count,
            'in_progress_count': in_progress_count,
            'resolved_count': resolved_count,
        })
        html = HTML(string=html_string, base_url=request.build_absolute_uri('/'))
        pdf = html.write_pdf()
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="complaint_report.pdf"'
        return response

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'complaint', 'notification_type', 'message', 'created_at', 'is_read')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('user__username', 'complaint__description', 'message')

