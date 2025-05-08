def decimal_to_dms(value, coord_type):
    is_positive = value >= 0
    value = abs(value)
    degrees = int(value)
    minutes = int((value - degrees) * 60)
    seconds = (value - degrees - minutes/60) * 3600
    if coord_type == 'lat':
        direction = 'N' if is_positive else 'S'
    else:
        direction = 'E' if is_positive else 'W'
    return f"{degrees}°{minutes}'{seconds:.1f}\"{direction}"
