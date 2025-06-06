from datetime import datetime
from app import db

class ParkingSpace(db.Model):
    __tablename__ = 'parking_spaces'
    
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.String(10), unique=True, nullable=False)  # Ej: "A1", "B5"
    floor = db.Column(db.Integer, nullable=False, default=1)
    is_occupied = db.Column(db.Boolean, nullable=False, default=False)
    space_type = db.Column(db.String(20), nullable=False, default='regular')  # regular, disabled, electric
    hourly_rate = db.Column(db.Float, nullable=False, default=2000.0)  # Precio por hora en pesos
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Relación con entradas y salidas
    sessions = db.relationship('ParkingSession', backref='space', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'number': self.number,
            'floor': self.floor,
            'is_occupied': self.is_occupied,
            'space_type': self.space_type,
            'hourly_rate': self.hourly_rate,
            'created_at': self.created_at.isoformat()
        }

class Vehicle(db.Model):
    __tablename__ = 'vehicles'
    
    id = db.Column(db.Integer, primary_key=True)
    license_plate = db.Column(db.String(10), unique=True, nullable=False)
    vehicle_type = db.Column(db.String(20), nullable=False)  # car, motorcycle, truck
    owner_name = db.Column(db.String(100), nullable=False)
    owner_phone = db.Column(db.String(15), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Relación con entradas y salidas
    sessions = db.relationship('ParkingSession', backref='vehicle', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'license_plate': self.license_plate,
            'vehicle_type': self.vehicle_type,
            'owner_name': self.owner_name,
            'owner_phone': self.owner_phone,
            'created_at': self.created_at.isoformat()
        }

class ParkingSession(db.Model):
    __tablename__ = 'parking_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'), nullable=False)
    space_id = db.Column(db.Integer, db.ForeignKey('parking_spaces.id'), nullable=False)
    entry_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    exit_time = db.Column(db.DateTime, nullable=True)
    total_hours = db.Column(db.Float, nullable=True)
    total_cost = db.Column(db.Float, nullable=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    payment_status = db.Column(db.String(20), nullable=False, default='pending')  # pending, paid
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    def calculate_cost(self):
        if self.exit_time and self.entry_time:
            duration = self.exit_time - self.entry_time
            hours = duration.total_seconds() / 3600
            self.total_hours = round(hours, 2)
            self.total_cost = round(hours * self.space.hourly_rate, 2)
            return self.total_cost
        return 0
    
    def to_dict(self):
        return {
            'id': self.id,
            'vehicle_id': self.vehicle_id,
            'space_id': self.space_id,
            'vehicle': self.vehicle.to_dict() if self.vehicle else None,
            'space': self.space.to_dict() if self.space else None,
            'entry_time': self.entry_time.isoformat(),
            'exit_time': self.exit_time.isoformat() if self.exit_time else None,
            'total_hours': self.total_hours,
            'total_cost': self.total_cost,
            'is_active': self.is_active,
            'payment_status': self.payment_status,
            'created_at': self.created_at.isoformat()
        }