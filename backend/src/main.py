import os
import sys
from datetime import timedelta
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from src.models.database import db
from src.routes.auth import auth_bp
from src.routes.customers import customers_bp
from src.routes.plans import plans_bp
from src.routes.subscriptions import subscriptions_bp
from src.routes.orders import orders_bp
from src.routes.deliveries import deliveries_bp
from src.routes.payments import payments_bp
from src.routes.reports import reports_bp
from src.routes.portal import portal_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))

# Configuration
app.config['SECRET_KEY'] = 'tiffin-crm-secret-key-change-in-production'
app.config['JWT_SECRET_KEY'] = 'jwt-secret-key-change-in-production'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=7)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
CORS(app, origins="*")  # Allow all origins for development
jwt = JWTManager(app)
db.init_app(app)
migrate = Migrate(app, db)

# Register blueprints
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

