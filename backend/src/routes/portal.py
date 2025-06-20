from flask import Blueprint, request, jsonify
from src.models.database import db, Customer, Subscription, Order, Payment
from datetime import datetime, date, timedelta
import random
import string

portal_bp = Blueprint('portal', __name__)

def generate_otp():
    """Generate a 6-digit OTP"""
    return ''.join(random.choices(string.digits, k=6))

# In a real implementation, you would store OTPs in Redis or database with expiration
# For demo purposes, we'll use a simple in-memory store
otp_store = {}

@portal_bp.route('/send-otp', methods=['POST'])
def send_otp():
    try:
        data = request.get_json()
        phone_number = data.get('phone_number')
        
        if not phone_number:
            return jsonify({
                'success': False,
                'message': 'Phone number is required'
            }), 400
        
        # Check if customer exists
        customer = Customer.query.filter_by(phone_number=phone_number).first()
        if not customer:
            return jsonify({
                'success': False,
                'message': 'Customer not found with this phone number'
            }), 404
        
        # Generate OTP
        otp = generate_otp()
        
        # Store OTP with expiration (5 minutes)
        otp_store[phone_number] = {
            'otp': otp,
            'expires_at': datetime.utcnow() + timedelta(minutes=5),
            'customer_id': customer.id
        }
        
        # In a real implementation, you would send SMS here
        # For demo purposes, we'll return the OTP (remove this in production)
        return jsonify({
            'success': True,
            'message': 'OTP sent successfully',
            'otp': otp  # Remove this in production
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to send OTP: {str(e)}'
        }), 500

@portal_bp.route('/verify-otp', methods=['POST'])
def verify_otp():
    try:
        data = request.get_json()
        phone_number = data.get('phone_number')
        otp = data.get('otp')
        
        if not phone_number or not otp:
            return jsonify({
                'success': False,
                'message': 'Phone number and OTP are required'
            }), 400
        
        # Check if OTP exists and is valid
        if phone_number not in otp_store:
            return jsonify({
                'success': False,
                'message': 'Invalid or expired OTP'
            }), 400
        
        stored_otp_data = otp_store[phone_number]
        
        # Check if OTP has expired
        if datetime.utcnow() > stored_otp_data['expires_at']:
            del otp_store[phone_number]
            return jsonify({
                'success': False,
                'message': 'OTP has expired'
            }), 400
        
        # Check if OTP matches
        if otp != stored_otp_data['otp']:
            return jsonify({
                'success': False,
                'message': 'Invalid OTP'
            }), 400
        
        # OTP is valid, get customer
        customer = Customer.query.get(stored_otp_data['customer_id'])
        
        # Clean up OTP
        del otp_store[phone_number]
        
        # In a real implementation, you would create a session token here
        # For demo purposes, we'll return customer data directly
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'data': {
                'customer': customer.to_dict(),
                'session_token': f"session_{customer.id}_{datetime.utcnow().timestamp()}"
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to verify OTP: {str(e)}'
        }), 500

@portal_bp.route('/profile/<int:customer_id>', methods=['GET'])
def get_customer_profile(customer_id):
    try:
        customer = Customer.query.get(customer_id)
        
        if not customer:
            return jsonify({
                'success': False,
                'message': 'Customer not found'
            }), 404
        
        # Get customer with additional info
        customer_data = customer.to_dict()
        
        # Get active subscriptions
        active_subscriptions = Subscription.query.filter(
            Subscription.customer_id == customer_id,
            Subscription.status == 'active'
        ).all()
        
        customer_data['active_subscriptions'] = [sub.to_dict() for sub in active_subscriptions]
        customer_data['total_active_subscriptions'] = len(active_subscriptions)
        
        return jsonify({
            'success': True,
            'data': customer_data
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to retrieve profile: {str(e)}'
        }), 500

@portal_bp.route('/orders/<int:customer_id>', methods=['GET'])
def get_customer_orders(customer_id):
    try:
        customer = Customer.query.get(customer_id)
        
        if not customer:
            return jsonify({
                'success': False,
                'message': 'Customer not found'
            }), 404
        
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 20, type=int)
        status = request.args.get('status')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        query = Order.query.filter(Order.customer_id == customer_id)
        
        if status:
            query = query.filter(Order.status == status)
        
        if start_date:
            query = query.filter(Order.order_date >= datetime.strptime(start_date, '%Y-%m-%d').date())
        
        if end_date:
            query = query.filter(Order.order_date <= datetime.strptime(end_date, '%Y-%m-%d').date())
        
        orders = query.order_by(Order.order_date.desc()).paginate(
            page=page, 
            per_page=limit, 
            error_out=False
        )
        
        result = []
        for order in orders.items:
            order_data = order.to_dict()
            order_data['plan_name'] = order.subscription.plan.name
            if order.delivery:
                order_data['delivery'] = order.delivery.to_dict()
            result.append(order_data)
        
        # Get upcoming orders (next 7 days)
        upcoming_orders = Order.query.filter(
            Order.customer_id == customer_id,
            Order.order_date > date.today(),
            Order.order_date <= date.today() + timedelta(days=7),
            Order.status.in_(['pending', 'preparing', 'prepared'])
        ).order_by(Order.order_date).all()
        
        upcoming_data = []
        for order in upcoming_orders:
            order_data = order.to_dict()
            order_data['plan_name'] = order.subscription.plan.name
            if order.delivery:
                order_data['delivery'] = order.delivery.to_dict()
            upcoming_data.append(order_data)
        
        return jsonify({
            'success': True,
            'data': {
                'orders': result,
                'upcoming_orders': upcoming_data,
                'pagination': {
                    'current_page': orders.page,
                    'total_pages': orders.pages,
                    'total_items': orders.total,
                    'items_per_page': orders.per_page,
                    'has_next': orders.has_next,
                    'has_prev': orders.has_prev
                }
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to retrieve orders: {str(e)}'
        }), 500

@portal_bp.route('/orders/<int:order_id>/cancel', methods=['POST'])
def cancel_customer_order(order_id):
    try:
        data = request.get_json()
        customer_id = data.get('customer_id')
        reason = data.get('reason', 'Customer cancellation')
        
        if not customer_id:
            return jsonify({
                'success': False,
                'message': 'Customer ID is required'
            }), 400
        
        order = Order.query.get(order_id)
        
        if not order:
            return jsonify({
                'success': False,
                'message': 'Order not found'
            }), 404
        
        # Verify order belongs to customer
        if order.customer_id != customer_id:
            return jsonify({
                'success': False,
                'message': 'Unauthorized to cancel this order'
            }), 403
        
        # Check if order can be cancelled (not delivered or out for delivery)
        if order.status in ['delivered', 'out_for_delivery']:
            return jsonify({
                'success': False,
                'message': 'Cannot cancel order that is already delivered or out for delivery'
            }), 400
        
        # Check if cancellation is within allowed time (e.g., before 8 AM on delivery date)
        if order.order_date == date.today():
            current_time = datetime.now().time()
            cutoff_time = datetime.strptime('08:00', '%H:%M').time()
            if current_time > cutoff_time:
                return jsonify({
                    'success': False,
                    'message': 'Cannot cancel order after 8:00 AM on delivery date'
                }), 400
        
        # Cancel the order
        order.status = 'cancelled'
        order.special_requests = f"Cancelled by customer: {reason}"
        order.updated_at = datetime.utcnow()
        
        # Cancel delivery if exists
        if order.delivery:
            order.delivery.delivery_status = 'cancelled'
            order.delivery.delivery_notes = f"Cancelled by customer: {reason}"
            order.delivery.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Order cancelled successfully',
            'data': order.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Failed to cancel order: {str(e)}'
        }), 500

@portal_bp.route('/payments/<int:customer_id>', methods=['GET'])
def get_customer_payments(customer_id):
    try:
        customer = Customer.query.get(customer_id)
        
        if not customer:
            return jsonify({
                'success': False,
                'message': 'Customer not found'
            }), 404
        
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 20, type=int)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        query = Payment.query.filter(Payment.customer_id == customer_id)
        
        if start_date:
            query = query.filter(Payment.payment_date >= datetime.strptime(start_date, '%Y-%m-%d'))
        
        if end_date:
            query = query.filter(Payment.payment_date <= datetime.strptime(end_date, '%Y-%m-%d'))
        
        payments = query.order_by(Payment.payment_date.desc()).paginate(
            page=page, 
            per_page=limit, 
            error_out=False
        )
        
        result = []
        for payment in payments.items:
            payment_data = payment.to_dict()
            if payment.subscription:
                payment_data['subscription'] = payment.subscription.to_dict()
                payment_data['plan_name'] = payment.subscription.plan.name
            result.append(payment_data)
        
        return jsonify({
            'success': True,
            'data': {
                'current_balance': float(customer.account_balance),
                'payments': result,
                'pagination': {
                    'current_page': payments.page,
                    'total_pages': payments.pages,
                    'total_items': payments.total,
                    'items_per_page': payments.per_page,
                    'has_next': payments.has_next,
                    'has_prev': payments.has_prev
                }
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to retrieve payments: {str(e)}'
        }), 500

@portal_bp.route('/subscriptions/<int:customer_id>', methods=['GET'])
def get_customer_subscriptions(customer_id):
    try:
        customer = Customer.query.get(customer_id)
        
        if not customer:
            return jsonify({
                'success': False,
                'message': 'Customer not found'
            }), 404
        
        subscriptions = Subscription.query.filter(Subscription.customer_id == customer_id).all()
        
        result = []
        for subscription in subscriptions:
            sub_data = subscription.to_dict()
            sub_data['plan'] = subscription.plan.to_dict()
            
            # Get recent orders for this subscription
            recent_orders = Order.query.filter(
                Order.subscription_id == subscription.id
            ).order_by(Order.order_date.desc()).limit(5).all()
            
            sub_data['recent_orders'] = [order.to_dict() for order in recent_orders]
            sub_data['total_orders'] = len(subscription.orders)
            
            result.append(sub_data)
        
        return jsonify({
            'success': True,
            'data': result
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to retrieve subscriptions: {str(e)}'
        }), 500

@portal_bp.route('/support', methods=['POST'])
def submit_support_request():
    try:
        data = request.get_json()
        customer_id = data.get('customer_id')
        subject = data.get('subject')
        message = data.get('message')
        priority = data.get('priority', 'medium')
        
        if not customer_id or not subject or not message:
            return jsonify({
                'success': False,
                'message': 'Customer ID, subject, and message are required'
            }), 400
        
        customer = Customer.query.get(customer_id)
        if not customer:
            return jsonify({
                'success': False,
                'message': 'Customer not found'
            }), 404
        
        # In a real implementation, you would save this to a support tickets table
        # For demo purposes, we'll just return success
        
        support_ticket = {
            'ticket_id': f"TKT-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            'customer_id': customer_id,
            'customer_name': f"{customer.first_name} {customer.last_name}",
            'subject': subject,
            'message': message,
            'priority': priority,
            'status': 'open',
            'created_at': datetime.utcnow().isoformat()
        }
        
        return jsonify({
            'success': True,
            'message': 'Support request submitted successfully',
            'data': support_ticket
        }), 201
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to submit support request: {str(e)}'
        }), 500

