import unittest
import json
import os
import sys
import tempfile

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db

class TestE2E(unittest.TestCase):
    
    def setUp(self):
        """Configurar aplicación y base de datos de prueba"""
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
    
    def test_get_spaces_returns_list_and_200(self):
        """
        Prueba E2E: GET /spaces retorna lista completa y código 200
        """
        # Primero crear algunos espacios usando POST
        spaces_data = [
            {
                'number': 'A1',
                'floor': 1,
                'space_type': 'regular',
                'hourly_rate': 2000.0
            },
            {
                'number': 'A2',
                'floor': 1,
                'space_type': 'disabled',
                'hourly_rate': 2000.0
            },
            {
                'number': 'B1',
                'floor': 2,
                'space_type': 'electric',
                'hourly_rate': 2500.0
            }
        ]
        
        # Crear espacios via API
        for space_data in spaces_data:
            response = self.client.post(
                '/api/spaces',
                data=json.dumps(space_data),
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 201)
        
        # Hacer GET para obtener todos los espacios
        response = self.client.get('/api/spaces')
        
        # Verificar código de estado
        self.assertEqual(response.status_code, 200)
        
        # Verificar que la respuesta sea JSON
        self.assertEqual(response.content_type, 'application/json')
        
        # Parsear respuesta
        data = json.loads(response.data)
        
        # Verificar que sea una lista
        self.assertIsInstance(data, list)
        
        # Verificar que contenga los 3 espacios
        self.assertEqual(len(data), 3)
        
        # Verificar estructura de cada espacio
        for space in data:
            self.assertIn('id', space)
            self.assertIn('number', space)
            self.assertIn('floor', space)
            self.assertIn('space_type', space)
            self.assertIn('hourly_rate', space)
            self.assertIn('is_occupied', space)
            self.assertIn('created_at', space)
        
        # Verificar datos específicos
        numbers = [space['number'] for space in data]
        self.assertIn('A1', numbers)
        self.assertIn('A2', numbers)
        self.assertIn('B1', numbers)
    
    def test_post_spaces_creates_element_and_returns_201(self):
        """
        Prueba E2E: POST /spaces crea elemento y retorna 201 con datos
        """
        # Datos del nuevo espacio
        new_space_data = {
            'number': 'C5',
            'floor': 3,
            'space_type': 'regular',
            'hourly_rate': 3000.0
        }
        
        # Hacer POST para crear el espacio
        response = self.client.post(
            '/api/spaces',
            data=json.dumps(new_space_data),
            content_type='application/json'
        )
        
        # Verificar código de estado 201 (Created)
        self.assertEqual(response.status_code, 201)
        
        # Verificar que la respuesta sea JSON
        self.assertEqual(response.content_type, 'application/json')
        
        # Parsear respuesta
        data = json.loads(response.data)
        
        # Verificar que sea un diccionario
        self.assertIsInstance(data, dict)
        
        # Verificar que contenga un ID asignado
        self.assertIn('id', data)
        self.assertIsNotNone(data['id'])
        
        # Verificar datos del espacio creado
        self.assertEqual(data['number'], 'C5')
        self.assertEqual(data['floor'], 3)
        self.assertEqual(data['space_type'], 'regular')
        self.assertEqual(data['hourly_rate'], 3000.0)
        self.assertFalse(data['is_occupied'])  # Debe estar desocupado por defecto
        
        # Verificar que se puede recuperar el espacio creado
        get_response = self.client.get(f"/api/spaces/{data['id']}")
        self.assertEqual(get_response.status_code, 200)
        
        retrieved_data = json.loads(get_response.data)
        self.assertEqual(retrieved_data['number'], 'C5')
    
    def test_delete_spaces_removes_element_and_returns_204_then_get_returns_404(self):
        """
        Prueba E2E: DELETE /spaces/:id elimina y retorna 204, luego GET retorna 404
        """
        # Primero crear un espacio
        space_data = {
            'number': 'D10',
            'floor': 4,
            'space_type': 'regular',
            'hourly_rate': 2200.0
        }
        
        # Crear el espacio
        create_response = self.client.post(
            '/api/spaces',
            data=json.dumps(space_data),
            content_type='application/json'
        )
        
        self.assertEqual(create_response.status_code, 201)
        created_space = json.loads(create_response.data)
        space_id = created_space['id']
        
        # Verificar que el espacio existe antes de eliminarlo
        get_response_before = self.client.get(f'/api/spaces/{space_id}')
        self.assertEqual(get_response_before.status_code, 200)
        
        # Eliminar el espacio
        delete_response = self.client.delete(f'/api/spaces/{space_id}')
        
        # Verificar código de estado 204 (No Content)
        self.assertEqual(delete_response.status_code, 204)
        
        # Verificar que la respuesta esté vacía
        self.assertEqual(delete_response.data, b'')
        
        # Intentar obtener el espacio eliminado - debe retornar 404
        get_response_after = self.client.get(f'/api/spaces/{space_id}')
        self.assertEqual(get_response_after.status_code, 404)
        
        # Verificar que el espacio ya no esté en la lista de espacios
        list_response = self.client.get('/api/spaces')
        self.assertEqual(list_response.status_code, 200)
        
        spaces_list = json.loads(list_response.data)
        space_ids = [space['id'] for space in spaces_list]
        self.assertNotIn(space_id, space_ids)

if __name__ == '__main__':
    unittest.main()