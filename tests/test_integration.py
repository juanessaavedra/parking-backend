import unittest
import os
import sys
import tempfile

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models.parking import ParkingSpace, Vehicle, ParkingSession

class TestIntegration(unittest.TestCase):
    
    def setUp(self):
        """Configurar base de datos de prueba antes de cada test"""
        # Crear archivo temporal para la base de datos de prueba
        self.db_fd, self.db_path = tempfile.mkstemp()
        
        # Configurar la aplicación para testing
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{self.db_path}'
        self.app.config['WTF_CSRF_ENABLED'] = False
        
        # Crear contexto de aplicación
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # Crear todas las tablas
        db.create_all()
        
        # Cliente de prueba
        self.client = self.app.test_client()
    
    def tearDown(self):
        """Limpiar después de cada test"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        os.close(self.db_fd)
        os.unlink(self.db_path)
    
    def test_insert_parking_space_to_database(self):
        """
        Prueba de integración: Insertar registro en base de datos
        Inserta un espacio de parking en la base de datos
        """
        # Crear un nuevo espacio de parking
        space = ParkingSpace(
            number='A1',
            floor=1,
            space_type='regular',
            hourly_rate=2000.0
        )
        
        # Insertar en la base de datos
        db.session.add(space)
        db.session.commit()
        
        # Verificar que se insertó correctamente
        self.assertIsNotNone(space.id)
        
        # Buscar en la base de datos
        found_space = ParkingSpace.query.filter_by(number='A1').first()
        
        # Verificaciones
        self.assertIsNotNone(found_space)
        self.assertEqual(found_space.number, 'A1')
        self.assertEqual(found_space.floor, 1)
        self.assertEqual(found_space.space_type, 'regular')
        self.assertEqual(found_space.hourly_rate, 2000.0)
        self.assertFalse(found_space.is_occupied)
    
    def test_query_vehicles_from_database(self):
        """
        Prueba de integración: Consultar registros de base de datos
        Inserta varios vehículos y los consulta
        """
        # Insertar varios vehículos de prueba
        vehicles_data = [
            {
                'license_plate': 'ABC123',
                'vehicle_type': 'car',
                'owner_name': 'Juan Pérez',
                'owner_phone': '3001234567'
            },
            {
                'license_plate': 'XYZ789',
                'vehicle_type': 'motorcycle',
                'owner_name': 'María García',
                'owner_phone': '3009876543'
            },
            {
                'license_plate': 'DEF456',
                'vehicle_type': 'truck',
                'owner_name': 'Carlos López',
                'owner_phone': None
            }
        ]
        
        # Insertar vehículos en la base de datos
        for vehicle_data in vehicles_data:
            vehicle = Vehicle(**vehicle_data)
            db.session.add(vehicle)
        
        db.session.commit()
        
        # Consultar todos los vehículos
        all_vehicles = Vehicle.query.all()
        self.assertEqual(len(all_vehicles), 3)
        
        # Consultar vehículo específico por placa
        specific_vehicle = Vehicle.query.filter_by(license_plate='ABC123').first()
        self.assertIsNotNone(specific_vehicle)
        self.assertEqual(specific_vehicle.owner_name, 'Juan Pérez')
        self.assertEqual(specific_vehicle.vehicle_type, 'car')
        
        # Consultar vehículos por tipo
        cars = Vehicle.query.filter_by(vehicle_type='car').all()
        self.assertEqual(len(cars), 1)
        self.assertEqual(cars[0].license_plate, 'ABC123')
        
        # Consultar vehículos con teléfono
        vehicles_with_phone = Vehicle.query.filter(Vehicle.owner_phone.isnot(None)).all()
        self.assertEqual(len(vehicles_with_phone), 2)
    
    def test_delete_parking_session_from_database(self):
        """
        Prueba de integración: Eliminar registro de base de datos
        Crea una sesión de parking y la elimina
        """
        # Primero crear un espacio y un vehículo
        space = ParkingSpace(
            number='B5',
            floor=2,
            space_type='regular',
            hourly_rate=2500.0
        )
        
        vehicle = Vehicle(
            license_plate='TEST123',
            vehicle_type='car',
            owner_name='Usuario Prueba',
            owner_phone='3001111111'
        )
        
        db.session.add(space)
        db.session.add(vehicle)
        db.session.commit()
        
        # Crear una sesión de parking
        session = ParkingSession(
            vehicle_id=vehicle.id,
            space_id=space.id
        )
        
        db.session.add(session)
        db.session.commit()
        
        # Verificar que la sesión se creó
        session_id = session.id
        found_session = ParkingSession.query.get(session_id)
        self.assertIsNotNone(found_session)
        self.assertTrue(found_session.is_active)
        
        # Verificar que hay 1 sesión en total
        total_sessions_before = ParkingSession.query.count()
        self.assertEqual(total_sessions_before, 1)
        
        # Eliminar la sesión
        db.session.delete(found_session)
        db.session.commit()
        
        # Verificar que se eliminó
        deleted_session = ParkingSession.query.get(session_id)
        self.assertIsNone(deleted_session)
        
        # Verificar que no hay sesiones
        total_sessions_after = ParkingSession.query.count()
        self.assertEqual(total_sessions_after, 0)
        
        # Verificar que el espacio y vehículo siguen existiendo
        remaining_space = ParkingSpace.query.get(space.id)
        remaining_vehicle = Vehicle.query.get(vehicle.id)
        self.assertIsNotNone(remaining_space)
        self.assertIsNotNone(remaining_vehicle)

if __name__ == '__main__':
    unittest.main()