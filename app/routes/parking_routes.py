from flask import Blueprint, request, jsonify
from datetime import datetime
from app import db
from app.models.parking import ParkingSpace, Vehicle, ParkingSession

parking_bp = Blueprint('parking', __name__)

# ============ ESPACIOS DE PARKING ============

@parking_bp.route('/spaces', methods=['GET'])
def get_all_spaces():
    """Obtener todos los espacios de parking"""
    spaces = ParkingSpace.query.all()
    return jsonify([space.to_dict() for space in spaces])

@parking_bp.route('/spaces', methods=['POST'])
def create_space():
    """Crear un nuevo espacio de parking"""
    data = request.get_json()
    
    # Validar datos requeridos
    if not data.get('number'):
        return jsonify({'error': 'El número del espacio es requerido'}), 400
    
    # Verificar si el espacio ya existe
    existing_space = ParkingSpace.query.filter_by(number=data['number']).first()
    if existing_space:
        return jsonify({'error': 'El espacio ya existe'}), 400
    
    space = ParkingSpace(
        number=data['number'],
        floor=data.get('floor', 1),
        space_type=data.get('space_type', 'regular'),
        hourly_rate=data.get('hourly_rate', 2000.0)
    )
    
    db.session.add(space)
    db.session.commit()
    
    return jsonify(space.to_dict()), 201

@parking_bp.route('/spaces/<int:space_id>', methods=['GET'])
def get_space(space_id):
    """Obtener un espacio específico"""
    space = ParkingSpace.query.get_or_404(space_id)
    return jsonify(space.to_dict())

@parking_bp.route('/spaces/<int:space_id>', methods=['DELETE'])
def delete_space(space_id):
    """Eliminar un espacio de parking"""
    space = ParkingSpace.query.get_or_404(space_id)
    
    # Verificar que no esté ocupado
    if space.is_occupied:
        return jsonify({'error': 'No se puede eliminar un espacio ocupado'}), 400
    
    # Verificar que no tenga sesiones activas
    active_sessions = ParkingSession.query.filter_by(space_id=space_id, is_active=True).first()
    if active_sessions:
        return jsonify({'error': 'No se puede eliminar un espacio con sesiones activas'}), 400
    
    db.session.delete(space)
    db.session.commit()
    
    return '', 204

@parking_bp.route('/spaces/available', methods=['GET'])
def get_available_spaces():
    """Obtener espacios disponibles"""
    spaces = ParkingSpace.query.filter_by(is_occupied=False).all()
    return jsonify([space.to_dict() for space in spaces])

# ============ VEHÍCULOS ============

@parking_bp.route('/vehicles', methods=['GET'])
def get_all_vehicles():
    """Obtener todos los vehículos"""
    vehicles = Vehicle.query.all()
    return jsonify([vehicle.to_dict() for vehicle in vehicles])

@parking_bp.route('/vehicles', methods=['POST'])
def create_vehicle():
    """Registrar un nuevo vehículo"""
    data = request.get_json()
    
    # Validar datos requeridos
    required_fields = ['license_plate', 'vehicle_type', 'owner_name']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'{field} es requerido'}), 400
    
    # Verificar si el vehículo ya existe
    existing_vehicle = Vehicle.query.filter_by(license_plate=data['license_plate']).first()
    if existing_vehicle:
        return jsonify({'error': 'El vehículo ya está registrado'}), 400
    
    vehicle = Vehicle(
        license_plate=data['license_plate'].upper(),
        vehicle_type=data['vehicle_type'],
        owner_name=data['owner_name'],
        owner_phone=data.get('owner_phone')
    )
    
    db.session.add(vehicle)
    db.session.commit()
    
    return jsonify(vehicle.to_dict()), 201

@parking_bp.route('/vehicles/<license_plate>', methods=['GET'])
def get_vehicle_by_plate(license_plate):
    """Obtener vehículo por placa"""
    vehicle = Vehicle.query.filter_by(license_plate=license_plate.upper()).first_or_404()
    return jsonify(vehicle.to_dict())

@parking_bp.route('/vehicles/<int:vehicle_id>', methods=['DELETE'])
def delete_vehicle(vehicle_id):
    """Eliminar un vehículo"""
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    
    # Verificar que no tenga sesiones activas
    active_sessions = ParkingSession.query.filter_by(vehicle_id=vehicle_id, is_active=True).first()
    if active_sessions:
        return jsonify({'error': 'No se puede eliminar un vehículo con sesiones activas'}), 400
    
    db.session.delete(vehicle)
    db.session.commit()
    
    return '', 204

# ============ SESIONES DE PARKING ============

@parking_bp.route('/sessions', methods=['GET'])
def get_all_sessions():
    """Obtener todas las sesiones de parking"""
    sessions = ParkingSession.query.all()
    return jsonify([session.to_dict() for session in sessions])

@parking_bp.route('/sessions/active', methods=['GET'])
def get_active_sessions():
    """Obtener sesiones activas"""
    sessions = ParkingSession.query.filter_by(is_active=True).all()
    return jsonify([session.to_dict() for session in sessions])

@parking_bp.route('/sessions/entry', methods=['POST'])
def vehicle_entry():
    """Registrar entrada de vehículo"""
    data = request.get_json()
    
    # Validar datos requeridos
    if not data.get('license_plate') or not data.get('space_id'):
        return jsonify({'error': 'Placa y espacio son requeridos'}), 400
    
    # Buscar o crear vehículo
    vehicle = Vehicle.query.filter_by(license_plate=data['license_plate'].upper()).first()
    if not vehicle:
        if not data.get('owner_name') or not data.get('vehicle_type'):
            return jsonify({'error': 'Para vehículos nuevos se requiere nombre del propietario y tipo de vehículo'}), 400
        
        vehicle = Vehicle(
            license_plate=data['license_plate'].upper(),
            vehicle_type=data['vehicle_type'],
            owner_name=data['owner_name'],
            owner_phone=data.get('owner_phone')
        )
        db.session.add(vehicle)
        db.session.flush()  # Para obtener el ID del vehículo
    
    # Verificar que el vehículo no tenga una sesión activa
    active_session = ParkingSession.query.filter_by(vehicle_id=vehicle.id, is_active=True).first()
    if active_session:
        return jsonify({'error': 'El vehículo ya tiene una sesión activa'}), 400
    
    # Verificar que el espacio esté disponible
    space = ParkingSpace.query.get_or_404(data['space_id'])
    if space.is_occupied:
        return jsonify({'error': 'El espacio ya está ocupado'}), 400
    
    # Crear sesión y ocupar espacio
    session = ParkingSession(
        vehicle_id=vehicle.id,
        space_id=space.id
    )
    
    space.is_occupied = True
    
    db.session.add(session)
    db.session.commit()
    
    return jsonify(session.to_dict()), 201

@parking_bp.route('/sessions/exit', methods=['POST'])
def vehicle_exit():
    """Registrar salida de vehículo"""
    data = request.get_json()
    
    if not data.get('license_plate'):
        return jsonify({'error': 'Placa es requerida'}), 400
    
    # Buscar vehículo y sesión activa
    vehicle = Vehicle.query.filter_by(license_plate=data['license_plate'].upper()).first_or_404()
    session = ParkingSession.query.filter_by(vehicle_id=vehicle.id, is_active=True).first()
    
    if not session:
        return jsonify({'error': 'No hay sesión activa para este vehículo'}), 400
    
    # Registrar salida
    session.exit_time = datetime.utcnow()
    session.is_active = False
    session.calculate_cost()
    
    # Liberar espacio
    space = ParkingSpace.query.get(session.space_id)
    space.is_occupied = False
    
    db.session.commit()
    
    return jsonify(session.to_dict())

@parking_bp.route('/sessions/<int:session_id>/pay', methods=['POST'])
def pay_session(session_id):
    """Marcar sesión como pagada"""
    session = ParkingSession.query.get_or_404(session_id)
    session.payment_status = 'paid'
    db.session.commit()
    
    return jsonify(session.to_dict())

# ============ ESTADÍSTICAS ============

@parking_bp.route('/stats', methods=['GET'])
def get_statistics():
    """Obtener estadísticas del parking"""
    total_spaces = ParkingSpace.query.count()
    occupied_spaces = ParkingSpace.query.filter_by(is_occupied=True).count()
    available_spaces = total_spaces - occupied_spaces
    active_sessions = ParkingSession.query.filter_by(is_active=True).count()
    total_vehicles = Vehicle.query.count()
    
    return jsonify({
        'total_spaces': total_spaces,
        'occupied_spaces': occupied_spaces,
        'available_spaces': available_spaces,
        'occupancy_rate': round((occupied_spaces / total_spaces * 100), 2) if total_spaces > 0 else 0,
        'active_sessions': active_sessions,
        'total_vehicles': total_vehicles
    })

# ============ ENDPOINTS DE PRUEBA ============

@parking_bp.route('/test', methods=['GET'])
def test_endpoint():
    """Endpoint de prueba"""
    return jsonify({
        'message': 'API de Parking funcionando correctamente',
        'timestamp': datetime.utcnow().isoformat(),
        'endpoints': [
            'GET /api/spaces - Obtener todos los espacios',
            'POST /api/spaces - Crear espacio',
            'DELETE /api/spaces/:id - Eliminar espacio',
            'GET /api/spaces/available - Espacios disponibles',
            'GET /api/vehicles - Obtener todos los vehículos',
            'POST /api/vehicles - Registrar vehículo',
            'DELETE /api/vehicles/:id - Eliminar vehículo',
            'GET /api/sessions - Obtener todas las sesiones',
            'GET /api/sessions/active - Sesiones activas',
            'POST /api/sessions/entry - Entrada de vehículo',
            'POST /api/sessions/exit - Salida de vehículo',
            'GET /api/stats - Estadísticas'
        ]
    })