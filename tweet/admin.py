from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from django.utils import timezone
from .models import Complaint, ComplaintImage
from django.utils.safestring import mark_safe
import datetime

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

