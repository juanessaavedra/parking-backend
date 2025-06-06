# Sistema de Parking - Backend API

Backend desarrollado en Flask para gestionar un sistema de parking con espacios y vehículos 

## 🚀 Instalación

### Prerrequisitos
- Python 3.8 o superior
- pip3

### Pasos de instalación

1. **Clonar/Descargar el proyecto**
```bash
cd parking-backend
```

2. **Crear entorno virtual**
```bash
python3 -m venv venv
```

3. **Activar entorno virtual**
```bash
source venv/bin/activate
```

4. **Instalar dependencias**
```bash
pip3 install -r requirements.txt
```

5. **Configurar variables de entorno** (Opcional)

6. **Ejecutar el servidor**
```bash
python3 run.py
```

El servidor estará disponible en: `http://localhost:5001`


## 🗄️ Base de Datos

El sistema utiliza SQLite con las siguientes tablas:

- **parking_spaces**: Espacios de parking
- **vehicles**: Vehículos registrados
- **parking_sessions**: Documenta cada vez que un vehiculo entra y sale

La base de datos se crea automáticamente al ejecutar la aplicación.

## 🔧 API Endpoints

### Base URL: `http://localhost:5001/api`

## 📋 Testing con Postman

### 1. **Prueba de Conexión**
- **Method:** `GET`
- **URL:** `http://localhost:5001/api/test`
- **Response:** Información de la API y lista de endpoints disponibles

### 2. **Estadísticas del Sistema**
- **Method:** `GET`
- **URL:** `http://localhost:5001/api/stats`
- **Response:** Estadísticas generales del parking

---

## 🅿️ Gestión de Espacios

### 3. **Crear Espacio de Parking**
- **Method:** `POST`
- **URL:** `http://localhost:5001/api/spaces`
- **Headers:** `Content-Type: application/json`
- **Body:**
```json
{
  "number": "A1",
  "floor": 1,
  "space_type": "regular",
  "hourly_rate": 2000
}
```

**Tipos de espacio disponibles:** `regular`, `disabled`, `electric`

### 4. **Obtener Todos los Espacios**
- **Method:** `GET`
- **URL:** `http://localhost:5001/api/spaces`

### 5. **Obtener Espacios Disponibles**
- **Method:** `GET`
- **URL:** `http://localhost:5001/api/spaces/available`

### 6. **Obtener Espacio Específico**
- **Method:** `GET`
- **URL:** `http://localhost:5001/api/spaces/{space_id}`

### 7. **Eliminar Espacio**
- **Method:** `DELETE`
- **URL:** `http://localhost:5001/api/spaces/{space_id}`
- **Response:** 204 (No Content) si se elimina exitosamente

---

## 🚗 Gestión de Vehículos

### 8. **Registrar Vehículo**
- **Method:** `POST`
- **URL:** `http://localhost:5001/api/vehicles`
- **Headers:** `Content-Type: application/json`
- **Body:**
```json
{
  "license_plate": "ABC123",
  "vehicle_type": "car",
  "owner_name": "Juan Pérez",
  "owner_phone": "3001234567"
}
```

**Tipos de vehículo:** `car`, `motorcycle`, `truck`

### 9. **Obtener Todos los Vehículos**
- **Method:** `GET`
- **URL:** `http://localhost:5001/api/vehicles`

### 10. **Buscar Vehículo por Placa**
- **Method:** `GET`
- **URL:** `http://localhost:5001/api/vehicles/{license_plate}`

### 11. **Eliminar Vehículo**
- **Method:** `DELETE`
- **URL:** `http://localhost:5001/api/vehicles/{vehicle_id}`
- **Response:** 204 (No Content) si se elimina exitosamente

---

## 🚪 Gestión de entradas (Entrada/Salida)

### 12. **Registrar Entrada de Vehículo**
- **Method:** `POST`
- **URL:** `http://localhost:5001/api/sessions/entry`
- **Headers:** `Content-Type: application/json`
- **Body (Vehículo existente):**
```json
{
  "license_plate": "ABC123",
  "space_id": 1
}
```

- **Body (Vehículo nuevo):**
```json
{
  "license_plate": "XYZ789",
  "space_id": 1,
  "owner_name": "María García",
  "vehicle_type": "car",
  "owner_phone": "3009876543"
}
```

### 13. **Registrar Salida de Vehículo**
- **Method:** `POST`
- **URL:** `http://localhost:5001/api/sessions/exit`
- **Headers:** `Content-Type: application/json`
- **Body:**
```json
{
  "license_plate": "ABC123"
}
```

### 14. **Obtener Todas las Sesiones**
- **Method:** `GET`
- **URL:** `http://localhost:5001/api/sessions`

### 15. **Obtener Sesiones Activas**
- **Method:** `GET`
- **URL:** `http://localhost:5001/api/sessions/active`

### 16. **Marcar Sesión como Pagada**
- **Method:** `POST`
- **URL:** `http://localhost:5001/api/sessions/{session_id}/pay`

---

## 🧪 Testing

El proyecto incluye una suite completa de pruebas automatizadas dividida en tres categorías:

```

### Ejecutar Pruebas

#### 1. **Todas las Pruebas**
```bash
python -m unittest discover tests -v
```

#### 2. **Solo Pruebas Unitarias**
```bash
python -m unittest tests.test_unit -v
```

#### 3. **Solo Pruebas de Integración**
```bash
python -m unittest tests.test_integration -v
```

#### 4. **Solo Pruebas End-to-End**
```bash
python -m unittest tests.test_e2e -v
```

#### 5. **Prueba Específica**
```bash
python -m unittest tests.test_unit.TestUnitFunctions.test_validate_required_fields -v
```

### Tipos de Pruebas

#### 🔧 **Pruebas Unitarias** (`test_unit.py`)
- **Validación de datos:** Prueba la función `validate_required_fields()`
- **Transformación de datos:** Prueba la función `calculate_hours_difference()`
- **Función utilitaria:** Prueba la función `generate_parking_receipt_id()`

#### 🔗 **Pruebas de Integración** (`test_integration.py`)
- **Insertar registro:** Prueba la inserción de espacios de parking en la base de datos
- **Consultar registros:** Prueba consultas múltiples de vehículos en la base de datos
- **Eliminar registro:** Prueba la eliminación de sesiones de parking de la base de datos

#### 🌐 **Pruebas End-to-End** (`test_e2e.py`)
- **GET /api/spaces:** Verifica que retorne lista completa con código 200
- **POST /api/spaces:** Verifica que cree elemento y retorne 201 con datos
- **DELETE /api/spaces/:id:** Verifica que elimine y retorne 204, luego GET retorne 404

