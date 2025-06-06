import unittest
from datetime import datetime
import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.utils import validate_required_fields, calculate_hours_difference, generate_parking_receipt_id

class TestUnitFunctions(unittest.TestCase):
    
    def test_validate_required_fields(self):
        """
        Prueba unitaria: Función de validación de datos de entrada
        """
        # Caso válido
        valid_data = {
            'license_plate': 'ABC123',
            'vehicle_type': 'car',
            'owner_name': 'Juan Pérez'
        }
        required_fields = ['license_plate', 'vehicle_type', 'owner_name']
        
        result = validate_required_fields(valid_data, required_fields)
        self.assertTrue(result)
        
        # Caso inválido - campo faltante
        invalid_data = {
            'license_plate': 'ABC123',
            'vehicle_type': 'car'
            # falta owner_name
        }
        
        result = validate_required_fields(invalid_data, required_fields)
        self.assertFalse(result)
        
        # Caso inválido - data no es diccionario
        result = validate_required_fields("invalid", required_fields)
        self.assertFalse(result)
    
    def test_calculate_hours_difference(self):
        """
        Prueba unitaria: Función de transformación de datos
        """
        # Caso 1: 2 horas exactas
        start = datetime(2024, 1, 1, 10, 0, 0)
        end = datetime(2024, 1, 1, 12, 0, 0)
        
        result = calculate_hours_difference(start, end)
        self.assertEqual(result, 2.0)
        
        # Caso 2: 30 minutos
        start = datetime(2024, 1, 1, 10, 0, 0)
        end = datetime(2024, 1, 1, 10, 30, 0)
        
        result = calculate_hours_difference(start, end)
        self.assertEqual(result, 0.5)
        
        # Caso 3: Tiempo inválido (end antes que start)
        start = datetime(2024, 1, 1, 12, 0, 0)
        end = datetime(2024, 1, 1, 10, 0, 0)
        
        result = calculate_hours_difference(start, end)
        self.assertEqual(result, 0)
    
    def test_generate_parking_receipt_id(self):
        """
        Prueba unitaria: Función utilitaria
        """
        # Generar varios IDs
        id1 = generate_parking_receipt_id()
        id2 = generate_parking_receipt_id()
        
        # Verificar que sean diferentes
        self.assertNotEqual(id1, id2)
        
        # Verificar formato
        self.assertTrue(id1.startswith('REC-'))
        self.assertTrue(id2.startswith('REC-'))
        
        # Verificar longitud (REC- + 8 caracteres)
        self.assertEqual(len(id1), 12)
        self.assertEqual(len(id2), 12)
        
        # Verificar que contenga solo caracteres válidos
        for char in id1[4:]:  # Después de 'REC-'
            self.assertTrue(char.isalnum())

if __name__ == '__main__':
    unittest.main()