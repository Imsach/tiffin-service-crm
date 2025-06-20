from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Customer(db.Model):
    __tablename__ = 'customers'
    
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True)
    address_line1 = db.Column(db.String(255), nullable=False)
    address_line2 = db.Column(db.String(255))
    city = db.Column(db.String(100), nullable=False)
    province = db.Column(db.String(100), nullable=False)
    postal_code = db.Column(db.String(10), nullable=False)
    delivery_instructions = db.Column(db.Text)
    dietary_restrictions = db.Column(db.Text)
    emergency_contact_name = db.Column(db.String(100))
    emergency_contact_phone = db.Column(db.String(20))
    account_balance = db.Column(db.Numeric(10, 2), default=0.00)
    status = db.Column(db.String(20), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    subscriptions = db.relationship('Subscription', backref='customer', lazy=True)
    orders = db.relationship('Order', backref='customer', lazy=True)
    payments = db.relationship('Payment', backref='customer', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'phone_number': self.phone_number,
            'email': self.email,
            'address_line1': self.address_line1,
            'address_line2': self.address_line2,
            'city': self.city,
            'province': self.province,
            'postal_code': self.postal_code,
            'delivery_instructions': self.delivery_instructions,
            'dietary_restrictions': self.dietary_restrictions,
            'emergency_contact_name': self.emergency_contact_name,
            'emergency_contact_phone': self.emergency_contact_phone,
            'account_balance': float(self.account_balance) if self.account_balance else 0.00,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Plan(db.Model):
    __tablename__ = 'plans'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    duration_days = db.Column(db.Integer, nullable=False)
    meals_per_week = db.Column(db.Integer, nullable=False)
    rotis_count = db.Column(db.Integer, nullable=False)
    rice_included = db.Column(db.Boolean, default=True)
    sabji_size_oz = db.Column(db.Integer, nullable=False)
    dal_kadhi_size_oz = db.Column(db.Integer, nullable=False)
    dessert_frequency = db.Column(db.String(50))
    includes_paan = db.Column(db.Boolean, default=False)
    includes_salad = db.Column(db.Boolean, default=True)
    includes_raita = db.Column(db.Boolean, default=True)
    includes_pickle = db.Column(db.Boolean, default=True)
    delivery_days = db.Column(db.String(100))
    is_trial = db.Column(db.Boolean, default=False)
    requires_student_id = db.Column(db.Boolean, default=False)
    status = db.Column(db.String(20), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    subscriptions = db.relationship('Subscription', backref='plan', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': float(self.price) if self.price else 0.00,
            'duration_days': self.duration_days,
            'meals_per_week': self.meals_per_week,
            'rotis_count': self.rotis_count,
            'rice_included': self.rice_included,
            'sabji_size_oz': self.sabji_size_oz,
            'dal_kadhi_size_oz': self.dal_kadhi_size_oz,
            'dessert_frequency': self.dessert_frequency,
            'includes_paan': self.includes_paan,
            'includes_salad': self.includes_salad,
            'includes_raita': self.includes_raita,
            'includes_pickle': self.includes_pickle,
            'delivery_days': self.delivery_days,
            'is_trial': self.is_trial,
            'requires_student_id': self.requires_student_id,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Subscription(db.Model):
    __tablename__ = 'subscriptions'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    plan_id = db.Column(db.Integer, db.ForeignKey('plans.id'), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date)
    status = db.Column(db.String(20), default='active')
    billing_cycle = db.Column(db.String(20), default='monthly')
    next_billing_date = db.Column(db.Date)
    auto_renew = db.Column(db.Boolean, default=True)
    pause_start_date = db.Column(db.Date)
    pause_end_date = db.Column(db.Date)
    cancellation_date = db.Column(db.Date)
    cancellation_reason = db.Column(db.Text)
    special_instructions = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    orders = db.relationship('Order', backref='subscription', lazy=True)
    payments = db.relationship('Payment', backref='subscription', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'plan_id': self.plan_id,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'status': self.status,
            'billing_cycle': self.billing_cycle,
            'next_billing_date': self.next_billing_date.isoformat() if self.next_billing_date else None,
            'auto_renew': self.auto_renew,
            'pause_start_date': self.pause_start_date.isoformat() if self.pause_start_date else None,
            'pause_end_date': self.pause_end_date.isoformat() if self.pause_end_date else None,
            'cancellation_date': self.cancellation_date.isoformat() if self.cancellation_date else None,
            'cancellation_reason': self.cancellation_reason,
            'special_instructions': self.special_instructions,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Order(db.Model):
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    subscription_id = db.Column(db.Integer, db.ForeignKey('subscriptions.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    order_date = db.Column(db.Date, nullable=False)
    meal_type = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), default='pending')
    preparation_notes = db.Column(db.Text)
    packing_notes = db.Column(db.Text)
    special_requests = db.Column(db.Text)
    total_amount = db.Column(db.Numeric(10, 2))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    delivery = db.relationship('Delivery', backref='order', uselist=False, lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'subscription_id': self.subscription_id,
            'customer_id': self.customer_id,
            'order_date': self.order_date.isoformat() if self.order_date else None,
            'meal_type': self.meal_type,
            'status': self.status,
            'preparation_notes': self.preparation_notes,
            'packing_notes': self.packing_notes,
            'special_requests': self.special_requests,
            'total_amount': float(self.total_amount) if self.total_amount else 0.00,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Delivery(db.Model):
    __tablename__ = 'deliveries'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    delivery_date = db.Column(db.Date, nullable=False)
    delivery_zone = db.Column(db.String(100))
    delivery_address = db.Column(db.Text, nullable=False)
    delivery_instructions = db.Column(db.Text)
    assigned_delivery_person_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    estimated_delivery_time = db.Column(db.Time)
    actual_delivery_time = db.Column(db.Time)
    delivery_status = db.Column(db.String(20), default='scheduled')
    route_sequence = db.Column(db.Integer)
    delivery_notes = db.Column(db.Text)
    customer_rating = db.Column(db.Integer)
    customer_feedback = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'delivery_date': self.delivery_date.isoformat() if self.delivery_date else None,
            'delivery_zone': self.delivery_zone,
            'delivery_address': self.delivery_address,
            'delivery_instructions': self.delivery_instructions,
            'assigned_delivery_person_id': self.assigned_delivery_person_id,
            'estimated_delivery_time': self.estimated_delivery_time.isoformat() if self.estimated_delivery_time else None,
            'actual_delivery_time': self.actual_delivery_time.isoformat() if self.actual_delivery_time else None,
            'delivery_status': self.delivery_status,
            'route_sequence': self.route_sequence,
            'delivery_notes': self.delivery_notes,
            'customer_rating': self.customer_rating,
            'customer_feedback': self.customer_feedback,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Payment(db.Model):
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    subscription_id = db.Column(db.Integer, db.ForeignKey('subscriptions.id'))
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    payment_type = db.Column(db.String(20), nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)
    transaction_id = db.Column(db.String(255))
    payment_status = db.Column(db.String(20), default='pending')
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'subscription_id': self.subscription_id,
            'amount': float(self.amount) if self.amount else 0.00,
            'payment_type': self.payment_type,
            'payment_method': self.payment_method,
            'transaction_id': self.transaction_id,
            'payment_status': self.payment_status,
            'payment_date': self.payment_date.isoformat() if self.payment_date else None,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(20))
    role = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), default='active')
    last_login = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    deliveries = db.relationship('Delivery', backref='delivery_person', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'phone_number': self.phone_number,
            'role': self.role,
            'status': self.status,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Inventory(db.Model):
    __tablename__ = 'inventory'
    
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(100))
    unit_of_measure = db.Column(db.String(50))
    current_stock = db.Column(db.Numeric(10, 3))
    minimum_stock = db.Column(db.Numeric(10, 3))
    cost_per_unit = db.Column(db.Numeric(10, 2))
    supplier_name = db.Column(db.String(255))
    last_restocked = db.Column(db.Date)
    expiry_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'item_name': self.item_name,
            'category': self.category,
            'unit_of_measure': self.unit_of_measure,
            'current_stock': float(self.current_stock) if self.current_stock else 0.00,
            'minimum_stock': float(self.minimum_stock) if self.minimum_stock else 0.00,
            'cost_per_unit': float(self.cost_per_unit) if self.cost_per_unit else 0.00,
            'supplier_name': self.supplier_name,
            'last_restocked': self.last_restocked.isoformat() if self.last_restocked else None,
            'expiry_date': self.expiry_date.isoformat() if self.expiry_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Expense(db.Model):
    __tablename__ = 'expenses'
    
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    expense_date = db.Column(db.Date, nullable=False)
    receipt_url = db.Column(db.String(500))
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'category': self.category,
            'description': self.description,
            'amount': float(self.amount) if self.amount else 0.00,
            'expense_date': self.expense_date.isoformat() if self.expense_date else None,
            'receipt_url': self.receipt_url,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

