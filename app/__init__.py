from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from app.config import Config

# Inicializar extensiones
db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Inicializar extensiones con la app
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app)
    
    # Registrar blueprints
    from app.routes.parking_routes import parking_bp
    app.register_blueprint(parking_bp, url_prefix='/api')
    
    # Crear tablas si no existen
    with app.app_context():
        db.create_all()
    
    return app