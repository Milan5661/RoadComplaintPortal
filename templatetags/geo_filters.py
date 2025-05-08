from django import template
from utils.geo import decimal_to_dms

register = template.Library()

@register.filter
def dms_lat(value):
    return decimal_to_dms(value, 'lat')

@register.filter
def dms_lon(value):
    return decimal_to_dms(value, 'lon')
