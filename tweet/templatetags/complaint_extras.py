from django import template

register = template.Library()

@register.filter
def count_status(queryset, status):
    """Count the number of complaints with a specific status."""
    return queryset.filter(status=status).count()
