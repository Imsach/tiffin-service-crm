from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.database import db, Customer
from datetime import datetime

customers_bp = Blueprint('customers', __name__)

@customers_bp.route('', methods=['GET'])
@jwt_required()
def get_customers():
    try:
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 20, type=int)
        status = request.args.get('status')
        search = request.args.get('search')
        sort = request.args.get('sort', 'created_at')
        order = request.args.get('order', 'desc')
        
        query = Customer.query
        
        # Apply filters
        if status:
            query = query.filter(Customer.status == status)
        
        if search:
            search_filter = f"%{search}%"
            query = query.filter(
                (Customer.first_name.ilike(search_filter)) |
                (Customer.last_name.ilike(search_filter)) |
                (Customer.phone_number.ilike(search_filter)) |
                (Customer.email.ilike(search_filter))
            )
        
        # Apply sorting
        if hasattr(Customer, sort):
            if order.lower() == 'desc':
                query = query.order_by(getattr(Customer, sort).desc())
            else:
                query = query.order_by(getattr(Customer, sort))
        
        # Paginate
        customers = query.paginate(
            page=page, 
            per_page=limit, 
            error_out=False
        )
        
        return jsonify({
            'success': True,
            'data': {
                'customers': [customer.to_dict() for customer in customers.items],
                'pagination': {
                    'current_page': customers.page,
                    'total_pages': customers.pages,
                    'total_items': customers.total,
                    'items_per_page': customers.per_page,
                    'has_next': customers.has_next,
                    'has_prev': customers.has_prev
                }
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to retrieve customers: {str(e)}'
        }), 500

@customers_bp.route('', methods=['POST'])
@jwt_required()
def create_customer():
    try:
        data = request.get_json()
        
        # Check if phone number already exists
        existing_customer = Customer.query.filter_by(phone_number=data.get('phone_number')).first()
        if existing_customer:
            return jsonify({
                'success': False,
                'message': 'Customer with this phone number already exists'
            }), 400
        
        # Check if email already exists (if provided)
        if data.get('email'):
            existing_email = Customer.query.filter_by(email=data.get('email')).first()
            if existing_email:
                return jsonify({
                    'success': False,
                    'message': 'Customer with this email already exists'
                }), 400
        
        new_customer = Customer(
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            phone_number=data.get('phone_number'),
            email=data.get('email'),
            address_line1=data.get('address_line1'),
            address_line2=data.get('address_line2'),
            city=data.get('city'),
            province=data.get('province'),
            postal_code=data.get('postal_code'),
            delivery_instructions=data.get('delivery_instructions'),
            dietary_restrictions=data.get('dietary_restrictions'),
            emergency_contact_name=data.get('emergency_contact_name'),
            emergency_contact_phone=data.get('emergency_contact_phone')
        )
        
        db.session.add(new_customer)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Customer created successfully',
            'data': new_customer.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Failed to create customer: {str(e)}'
        }), 500

@customers_bp.route('/<int:customer_id>', methods=['GET'])
@jwt_required()
def get_customer(customer_id):
    try:
        customer = Customer.query.get(customer_id)
        
        if not customer:
            return jsonify({
                'success': False,
                'message': 'Customer not found'
            }), 404
        
        # Get customer with related data
        customer_data = customer.to_dict()
        customer_data['active_subscriptions'] = len([s for s in customer.subscriptions if s.status == 'active'])
        customer_data['total_orders'] = len(customer.orders)
        customer_data['total_payments'] = len(customer.payments)
        
        return jsonify({
            'success': True,
            'data': customer_data
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to retrieve customer: {str(e)}'
        }), 500

@customers_bp.route('/<int:customer_id>', methods=['PUT'])
@jwt_required()
def update_customer(customer_id):
    try:
        customer = Customer.query.get(customer_id)
        
        if not customer:
            return jsonify({
                'success': False,
                'message': 'Customer not found'
            }), 404
        
        data = request.get_json()
        
        # Check if phone number is being changed and if it already exists
        if data.get('phone_number') and data.get('phone_number') != customer.phone_number:
            existing_customer = Customer.query.filter_by(phone_number=data.get('phone_number')).first()
            if existing_customer:
                return jsonify({
                    'success': False,
                    'message': 'Customer with this phone number already exists'
                }), 400
        
        # Check if email is being changed and if it already exists
        if data.get('email') and data.get('email') != customer.email:
            existing_email = Customer.query.filter_by(email=data.get('email')).first()
            if existing_email:
                return jsonify({
                    'success': False,
                    'message': 'Customer with this email already exists'
                }), 400
        
        # Update customer fields
        for field in ['first_name', 'last_name', 'phone_number', 'email', 'address_line1', 
                     'address_line2', 'city', 'province', 'postal_code', 'delivery_instructions',
                     'dietary_restrictions', 'emergency_contact_name', 'emergency_contact_phone', 'status']:
            if field in data:
                setattr(customer, field, data[field])
        
        customer.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Customer updated successfully',
            'data': customer.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Failed to update customer: {str(e)}'
        }), 500

@customers_bp.route('/<int:customer_id>', methods=['DELETE'])
@jwt_required()
def delete_customer(customer_id):
    try:
        customer = Customer.query.get(customer_id)
        
        if not customer:
            return jsonify({
                'success': False,
                'message': 'Customer not found'
            }), 404
        
        # Soft delete - set status to inactive
        customer.status = 'inactive'
        customer.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Customer deactivated successfully'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Failed to delete customer: {str(e)}'
        }), 500

@customers_bp.route('/<int:customer_id>/balance', methods=['GET'])
@jwt_required()
def get_customer_balance(customer_id):
    try:
        customer = Customer.query.get(customer_id)
        
        if not customer:
            return jsonify({
                'success': False,
                'message': 'Customer not found'
            }), 404
        
        # Get recent transactions
        recent_payments = [payment.to_dict() for payment in customer.payments[-10:]]
        
        return jsonify({
            'success': True,
            'data': {
                'customer_id': customer_id,
                'current_balance': float(customer.account_balance),
                'recent_transactions': recent_payments
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to retrieve customer balance: {str(e)}'
        }), 500

@customers_bp.route('/<int:customer_id>/add-balance', methods=['POST'])
@jwt_required()
def add_customer_balance(customer_id):
    try:
        customer = Customer.query.get(customer_id)
        
        if not customer:
            return jsonify({
                'success': False,
                'message': 'Customer not found'
            }), 404
        
        data = request.get_json()
        amount = data.get('amount')
        
        if not amount or amount <= 0:
            return jsonify({
                'success': False,
                'message': 'Valid amount is required'
            }), 400
        
        # Update customer balance
        customer.account_balance = float(customer.account_balance) + amount
        customer.updated_at = datetime.utcnow()
        
        # Create payment record
        from src.models.database import Payment
        payment = Payment(
            customer_id=customer_id,
            amount=amount,
            payment_type='balance_addition',
            payment_method=data.get('payment_method', 'cash'),
            payment_status='completed',
            description=data.get('description', 'Balance addition')
        )
        
        db.session.add(payment)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Balance added successfully',
            'data': {
                'new_balance': float(customer.account_balance),
                'amount_added': amount
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Failed to add balance: {str(e)}'
        }), 500

