def validate_required_fields(data, required_fields):
    """
    Valida que los campos requeridos estén presentes en los datos
    """
    if not data or not isinstance(data, dict):
        return False
    
    for field in required_fields:
        if field not in data or not data[field]:
            return False
    
    return True

def calculate_hours_difference(start_time, end_time):
    """
    Calcula la diferencia en horas entre dos fechas
    """
    if not start_time or not end_time:
        return 0
    
    if end_time <= start_time:
        return 0
    
    duration = end_time - start_time
    hours = duration.total_seconds() / 3600
    return round(hours, 2)

def generate_parking_receipt_id():
    """
    Genera un ID único para recibos de parking
    """
    import uuid
    return f"REC-{str(uuid.uuid4())[:8].upper()}"