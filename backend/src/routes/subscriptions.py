from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from src.models.database import db, Subscription, Customer, Plan
from datetime import datetime, date, timedelta

subscriptions_bp = Blueprint('subscriptions', __name__)

@subscriptions_bp.route('', methods=['GET'])
@jwt_required()
def get_subscriptions():
    try:
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 20, type=int)
        status = request.args.get('status')
        customer_id = request.args.get('customer_id', type=int)
        
        query = Subscription.query
        
        if status:
            query = query.filter(Subscription.status == status)
        
        if customer_id:
            query = query.filter(Subscription.customer_id == customer_id)
        
        # Join with customer and plan for additional info
        query = query.join(Customer).join(Plan)
        
        subscriptions = query.order_by(Subscription.created_at.desc()).paginate(
            page=page, 
            per_page=limit, 
            error_out=False
        )
        
        result = []
        for subscription in subscriptions.items:
            sub_data = subscription.to_dict()
            sub_data['customer_name'] = f"{subscription.customer.first_name} {subscription.customer.last_name}"
            sub_data['plan_name'] = subscription.plan.name
            sub_data['plan_price'] = float(subscription.plan.price)
            result.append(sub_data)
        
        return jsonify({
            'success': True,
            'data': {
                'subscriptions': result,
                'pagination': {
                    'current_page': subscriptions.page,
                    'total_pages': subscriptions.pages,
                    'total_items': subscriptions.total,
                    'items_per_page': subscriptions.per_page,
                    'has_next': subscriptions.has_next,
                    'has_prev': subscriptions.has_prev
                }
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to retrieve subscriptions: {str(e)}'
        }), 500

@subscriptions_bp.route('', methods=['POST'])
@jwt_required()
def create_subscription():
    try:
        data = request.get_json()
        
        # Validate customer exists
        customer = Customer.query.get(data.get('customer_id'))
        if not customer:
            return jsonify({
                'success': False,
                'message': 'Customer not found'
            }), 404
        
        # Validate plan exists
        plan = Plan.query.get(data.get('plan_id'))
        if not plan:
            return jsonify({
                'success': False,
                'message': 'Plan not found'
            }), 404
        
        # Calculate end date based on plan duration
        start_date = datetime.strptime(data.get('start_date'), '%Y-%m-%d').date()
        end_date = start_date + timedelta(days=plan.duration_days)
        
        # Calculate next billing date
        billing_cycle = data.get('billing_cycle', 'monthly')
        if billing_cycle == 'monthly':
            next_billing_date = start_date + timedelta(days=30)
        elif billing_cycle == 'weekly':
            next_billing_date = start_date + timedelta(days=7)
        else:
            next_billing_date = end_date
        
        new_subscription = Subscription(
            customer_id=data.get('customer_id'),
            plan_id=data.get('plan_id'),
            start_date=start_date,
            end_date=end_date,
            billing_cycle=billing_cycle,
            next_billing_date=next_billing_date,
            auto_renew=data.get('auto_renew', True),
            special_instructions=data.get('special_instructions')
        )
        
        db.session.add(new_subscription)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Subscription created successfully',
            'data': new_subscription.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Failed to create subscription: {str(e)}'
        }), 500

@subscriptions_bp.route('/<int:subscription_id>', methods=['GET'])
@jwt_required()
def get_subscription(subscription_id):
    try:
        subscription = Subscription.query.get(subscription_id)
        
        if not subscription:
            return jsonify({
                'success': False,
                'message': 'Subscription not found'
            }), 404
        
        # Get subscription with related data
        sub_data = subscription.to_dict()
        sub_data['customer'] = subscription.customer.to_dict()
        sub_data['plan'] = subscription.plan.to_dict()
        sub_data['total_orders'] = len(subscription.orders)
        sub_data['completed_orders'] = len([o for o in subscription.orders if o.status == 'delivered'])
        
        return jsonify({
            'success': True,
            'data': sub_data
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to retrieve subscription: {str(e)}'
        }), 500

@subscriptions_bp.route('/<int:subscription_id>', methods=['PUT'])
@jwt_required()
def update_subscription(subscription_id):
    try:
        subscription = Subscription.query.get(subscription_id)
        
        if not subscription:
            return jsonify({
                'success': False,
                'message': 'Subscription not found'
            }), 404
        
        data = request.get_json()
        
        # Update subscription fields
        for field in ['status', 'billing_cycle', 'auto_renew', 'special_instructions']:
            if field in data:
                setattr(subscription, field, data[field])
        
        # Handle date fields
        if 'end_date' in data and data['end_date']:
            subscription.end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()
        
        if 'next_billing_date' in data and data['next_billing_date']:
            subscription.next_billing_date = datetime.strptime(data['next_billing_date'], '%Y-%m-%d').date()
        
        subscription.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Subscription updated successfully',
            'data': subscription.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Failed to update subscription: {str(e)}'
        }), 500

@subscriptions_bp.route('/<int:subscription_id>/pause', methods=['POST'])
@jwt_required()
def pause_subscription(subscription_id):
    try:
        subscription = Subscription.query.get(subscription_id)
        
        if not subscription:
            return jsonify({
                'success': False,
                'message': 'Subscription not found'
            }), 404
        
        data = request.get_json()
        
        pause_start = datetime.strptime(data.get('pause_start_date'), '%Y-%m-%d').date()
        pause_end = datetime.strptime(data.get('pause_end_date'), '%Y-%m-%d').date()
        
        if pause_start >= pause_end:
            return jsonify({
                'success': False,
                'message': 'Pause end date must be after start date'
            }), 400
        
        subscription.status = 'paused'
        subscription.pause_start_date = pause_start
        subscription.pause_end_date = pause_end
        subscription.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Subscription paused successfully',
            'data': subscription.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Failed to pause subscription: {str(e)}'
        }), 500

@subscriptions_bp.route('/<int:subscription_id>/resume', methods=['POST'])
@jwt_required()
def resume_subscription(subscription_id):
    try:
        subscription = Subscription.query.get(subscription_id)
        
        if not subscription:
            return jsonify({
                'success': False,
                'message': 'Subscription not found'
            }), 404
        
        subscription.status = 'active'
        subscription.pause_start_date = None
        subscription.pause_end_date = None
        subscription.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Subscription resumed successfully',
            'data': subscription.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Failed to resume subscription: {str(e)}'
        }), 500

@subscriptions_bp.route('/<int:subscription_id>/cancel', methods=['POST'])
@jwt_required()
def cancel_subscription(subscription_id):
    try:
        subscription = Subscription.query.get(subscription_id)
        
        if not subscription:
            return jsonify({
                'success': False,
                'message': 'Subscription not found'
            }), 404
        
        data = request.get_json()
        
        subscription.status = 'cancelled'
        subscription.cancellation_date = date.today()
        subscription.cancellation_reason = data.get('reason', 'Customer request')
        subscription.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Subscription cancelled successfully',
            'data': subscription.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Failed to cancel subscription: {str(e)}'
        }), 500

@subscriptions_bp.route('/active', methods=['GET'])
@jwt_required()
def get_active_subscriptions():
    try:
        today = date.today()
        
        # Get all active subscriptions that are not paused and within date range
        active_subscriptions = Subscription.query.filter(
            Subscription.status == 'active',
            Subscription.start_date <= today,
            (Subscription.end_date.is_(None)) | (Subscription.end_date >= today),
            (Subscription.pause_start_date.is_(None)) | 
            (Subscription.pause_start_date > today) |
            (Subscription.pause_end_date < today)
        ).join(Customer).join(Plan).all()
        
        result = []
        for subscription in active_subscriptions:
            sub_data = subscription.to_dict()
            sub_data['customer_name'] = f"{subscription.customer.first_name} {subscription.customer.last_name}"
            sub_data['customer_phone'] = subscription.customer.phone_number
            sub_data['customer_address'] = f"{subscription.customer.address_line1}, {subscription.customer.city}"
            sub_data['plan_name'] = subscription.plan.name
            sub_data['meals_per_week'] = subscription.plan.meals_per_week
            result.append(sub_data)
        
        return jsonify({
            'success': True,
            'data': result
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to retrieve active subscriptions: {str(e)}'
        }), 500

