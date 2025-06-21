import os
import sys
from datetime import datetime
from flask import Flask, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Import configuration
from src.config import get_config

# Initialize Flask extensions
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

def create_app():
    """Application factory pattern."""
    app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
    
    # Load configuration
    config_class = get_config()
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    
    # Configure CORS
    CORS(app, origins=app.config['CORS_ORIGINS'])
    
    # Import models to ensure they're registered
    from src.models.database import User, Customer, Plan, Subscription, Order, Delivery, Payment
    
    # Register blueprints
    from src.routes.auth import auth_bp
    from src.routes.customers import customers_bp
    from src.routes.plans import plans_bp
    from src.routes.subscriptions import subscriptions_bp
    from src.routes.orders import orders_bp
    from src.routes.deliveries import deliveries_bp
    from src.routes.payments import payments_bp
    from src.routes.reports import reports_bp
    from src.routes.portal import portal_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(customers_bp, url_prefix='/api/customers')
    app.register_blueprint(plans_bp, url_prefix='/api/plans')
    app.register_blueprint(subscriptions_bp, url_prefix='/api/subscriptions')
    app.register_blueprint(orders_bp, url_prefix='/api/orders')
    app.register_blueprint(deliveries_bp, url_prefix='/api/deliveries')
    app.register_blueprint(payments_bp, url_prefix='/api/payments')
    app.register_blueprint(reports_bp, url_prefix='/api/reports')
    app.register_blueprint(portal_bp, url_prefix='/api/portal')
    
    # Create database tables
    with app.app_context():
        db.create_all()
        
        # Initialize default data if needed
        initialize_default_data()
    
    # Static file serving
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve(path):
        static_folder_path = app.static_folder
        if static_folder_path is None:
            return "Static folder not configured", 404

        if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
            return send_from_directory(static_folder_path, path)
        else:
            index_path = os.path.join(static_folder_path, 'index.html')
            if os.path.exists(index_path):
                return send_from_directory(static_folder_path, 'index.html')
            else:
                return "index.html not found", 404
    
    return app

def initialize_default_data():
    """Initialize default data for the application."""
    from src.models.database import User, Plan
    from werkzeug.security import generate_password_hash
    
    # Create default admin user if it doesn't exist
    admin_user = User.query.filter_by(username='admin').first()
    if not admin_user:
        admin_user = User(
            username='admin',
            email='admin@tiffincrm.com',
            password_hash=generate_password_hash('admin123'),
            first_name='Admin',
            last_name='User',
            role='administrator',
            is_active=True
        )
        db.session.add(admin_user)
    
    # Create default plans if they don't exist
    if Plan.query.count() == 0:
        default_plans = [
            {
                'name': 'Silver Plan',
                'description': '6-days a week, 24 tiffins per month',
                'price': 240.00,
                'duration_days': 30,
                'meals_per_week': 6,
                'rotis_count': 5,
                'rice_included': True,
                'sabji_size_oz': 8,
                'dal_kadhi_size_oz': 8,
                'dessert_frequency': 'weekly',
                'includes_paan': False,
                'includes_salad': True,
                'includes_raita': True,
                'includes_pickle': True,
                'delivery_days': 'Tuesday-Sunday',
                'is_trial': False,
                'requires_student_id': False
            },
            {
                'name': 'Gold Plan',
                'description': '6-days a week, 24 tiffins per month with extra portions',
                'price': 285.00,
                'duration_days': 30,
                'meals_per_week': 6,
                'rotis_count': 8,
                'rice_included': True,
                'sabji_size_oz': 12,
                'dal_kadhi_size_oz': 12,
                'dessert_frequency': 'weekly',
                'includes_paan': True,
                'includes_salad': True,
                'includes_raita': True,
                'includes_pickle': True,
                'delivery_days': 'Tuesday-Sunday',
                'is_trial': False,
                'requires_student_id': False
            },
            {
                'name': 'Student Plan',
                'description': 'Discounted Silver Plan for students',
                'price': 220.00,
                'duration_days': 30,
                'meals_per_week': 6,
                'rotis_count': 5,
                'rice_included': True,
                'sabji_size_oz': 8,
                'dal_kadhi_size_oz': 8,
                'dessert_frequency': 'weekly',
                'includes_paan': False,
                'includes_salad': True,
                'includes_raita': True,
                'includes_pickle': True,
                'delivery_days': 'Tuesday-Sunday',
                'is_trial': False,
                'requires_student_id': True
            },
            {
                'name': '6-Day Trial',
                'description': 'Experience the service before committing',
                'price': 90.00,
                'duration_days': 6,
                'meals_per_week': 6,
                'rotis_count': 5,
                'rice_included': True,
                'sabji_size_oz': 8,
                'dal_kadhi_size_oz': 8,
                'dessert_frequency': 'once',
                'includes_paan': False,
                'includes_salad': True,
                'includes_raita': True,
                'includes_pickle': True,
                'delivery_days': 'Tuesday-Sunday',
                'is_trial': True,
                'requires_student_id': False
            },
            {
                'name': '1-Day Trial',
                'description': 'Single day trial option',
                'price': 15.00,
                'duration_days': 1,
                'meals_per_week': 1,
                'rotis_count': 5,
                'rice_included': True,
                'sabji_size_oz': 8,
                'dal_kadhi_size_oz': 8,
                'dessert_frequency': 'none',
                'includes_paan': False,
                'includes_salad': True,
                'includes_raita': True,
                'includes_pickle': True,
                'delivery_days': 'Any day',
                'is_trial': True,
                'requires_student_id': False
            }
        ]
        
        for plan_data in default_plans:
            plan = Plan(**plan_data)
            db.session.add(plan)
    
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error initializing default data: {e}")

# Create the Flask application
app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    host = os.environ.get('HOST', '0.0.0.0')
    debug = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    print(f"Starting Tiffin CRM Server on {host}:{port}")
    print(f"Environment: {os.environ.get('FLASK_ENV', 'development')}")
    print(f"Database: {app.config['SQLALCHEMY_DATABASE_URI']}")
    
    app.run(host=host, port=port, debug=debug)

