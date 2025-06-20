from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from src.models.database import db, Order, Subscription, Customer, Plan, Delivery
from datetime import datetime, date

orders_bp = Blueprint('orders', __name__)

@orders_bp.route('', methods=['GET'])
@jwt_required()
def get_orders():
    try:
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 20, type=int)
        order_date = request.args.get('order_date')
        status = request.args.get('status')
        customer_id = request.args.get('customer_id', type=int)
        
        query = Order.query
        
        if order_date:
            query = query.filter(Order.order_date == datetime.strptime(order_date, '%Y-%m-%d').date())
        
        if status:
            query = query.filter(Order.status == status)
        
        if customer_id:
            query = query.filter(Order.customer_id == customer_id)
        
        # Join with related tables for additional info
        query = query.join(Customer).join(Subscription).join(Plan)
        
        orders = query.order_by(Order.order_date.desc(), Order.created_at.desc()).paginate(
            page=page, 
            per_page=limit, 
            error_out=False
        )
        
        result = []
        for order in orders.items:
            order_data = order.to_dict()
            order_data['customer_name'] = f"{order.customer.first_name} {order.customer.last_name}"
            order_data['customer_phone'] = order.customer.phone_number
            order_data['customer_address'] = f"{order.customer.address_line1}, {order.customer.city}"
            order_data['plan_name'] = order.subscription.plan.name
            order_data['delivery_status'] = order.delivery.delivery_status if order.delivery else 'not_scheduled'
            result.append(order_data)
        
        return jsonify({
            'success': True,
            'data': {
                'orders': result,
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

@orders_bp.route('/bulk-create', methods=['POST'])
@jwt_required()
def bulk_create_orders():
    try:
        data = request.get_json()
        order_date_str = data.get('order_date')
        meal_type = data.get('meal_type', 'lunch')
        exclude_customers = data.get('exclude_customers', [])
        
        if not order_date_str:
            return jsonify({
                'success': False,
                'message': 'Order date is required'
            }), 400
        
        order_date = datetime.strptime(order_date_str, '%Y-%m-%d').date()
        
        # Get all active subscriptions for the date
        active_subscriptions = Subscription.query.filter(
            Subscription.status == 'active',
            Subscription.start_date <= order_date,
            (Subscription.end_date.is_(None)) | (Subscription.end_date >= order_date),
            (Subscription.pause_start_date.is_(None)) | 
            (Subscription.pause_start_date > order_date) |
            (Subscription.pause_end_date < order_date)
        ).join(Customer).join(Plan).all()
        
        # Filter out excluded customers
        if exclude_customers:
            active_subscriptions = [s for s in active_subscriptions if s.customer_id not in exclude_customers]
        
        # Check if orders already exist for this date
        existing_orders = Order.query.filter(
            Order.order_date == order_date,
            Order.meal_type == meal_type
        ).all()
        
        existing_customer_ids = [o.customer_id for o in existing_orders]
        
        created_orders = []
        skipped_customers = []
        
        for subscription in active_subscriptions:
            # Skip if order already exists for this customer and date
            if subscription.customer_id in existing_customer_ids:
                skipped_customers.append({
                    'customer_id': subscription.customer_id,
                    'customer_name': f"{subscription.customer.first_name} {subscription.customer.last_name}",
                    'reason': 'Order already exists'
                })
                continue
            
            # Create order
            new_order = Order(
                subscription_id=subscription.id,
                customer_id=subscription.customer_id,
                order_date=order_date,
                meal_type=meal_type,
                status='pending',
                total_amount=subscription.plan.price / subscription.plan.meals_per_week  # Daily rate
            )
            
            db.session.add(new_order)
            db.session.flush()  # Get the order ID
            
            # Create delivery record
            delivery_address = f"{subscription.customer.address_line1}"
            if subscription.customer.address_line2:
                delivery_address += f", {subscription.customer.address_line2}"
            delivery_address += f", {subscription.customer.city}, {subscription.customer.province} {subscription.customer.postal_code}"
            
            new_delivery = Delivery(
                order_id=new_order.id,
                delivery_date=order_date,
                delivery_zone=subscription.customer.city,  # Use city as zone for now
                delivery_address=delivery_address,
                delivery_instructions=subscription.customer.delivery_instructions,
                delivery_status='scheduled'
            )
            
            db.session.add(new_delivery)
            created_orders.append(new_order.to_dict())
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Successfully created {len(created_orders)} orders',
            'data': {
                'created_orders': len(created_orders),
                'skipped_customers': len(skipped_customers),
                'order_date': order_date_str,
                'meal_type': meal_type,
                'orders': created_orders,
                'skipped': skipped_customers
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Failed to create bulk orders: {str(e)}'
        }), 500

@orders_bp.route('/<int:order_id>', methods=['GET'])
@jwt_required()
def get_order(order_id):
    try:
        order = Order.query.get(order_id)
        
        if not order:
            return jsonify({
                'success': False,
                'message': 'Order not found'
            }), 404
        
        # Get order with related data
        order_data = order.to_dict()
        order_data['customer'] = order.customer.to_dict()
        order_data['subscription'] = order.subscription.to_dict()
        order_data['plan'] = order.subscription.plan.to_dict()
        if order.delivery:
            order_data['delivery'] = order.delivery.to_dict()
        
        return jsonify({
            'success': True,
            'data': order_data
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to retrieve order: {str(e)}'
        }), 500

@orders_bp.route('/<int:order_id>/status', methods=['PUT'])
@jwt_required()
def update_order_status(order_id):
    try:
        order = Order.query.get(order_id)
        
        if not order:
            return jsonify({
                'success': False,
                'message': 'Order not found'
            }), 404
        
        data = request.get_json()
        new_status = data.get('status')
        notes = data.get('notes')
        
        if not new_status:
            return jsonify({
                'success': False,
                'message': 'Status is required'
            }), 400
        
        valid_statuses = ['pending', 'preparing', 'prepared', 'packed', 'out_for_delivery', 'delivered', 'cancelled']
        if new_status not in valid_statuses:
            return jsonify({
                'success': False,
                'message': f'Invalid status. Valid statuses: {", ".join(valid_statuses)}'
            }), 400
        
        order.status = new_status
        order.updated_at = datetime.utcnow()
        
        # Update notes based on status
        if new_status == 'preparing' and notes:
            order.preparation_notes = notes
        elif new_status == 'packed' and notes:
            order.packing_notes = notes
        
        # Update delivery status if exists
        if order.delivery:
            if new_status == 'out_for_delivery':
                order.delivery.delivery_status = 'in_transit'
            elif new_status == 'delivered':
                order.delivery.delivery_status = 'delivered'
                order.delivery.actual_delivery_time = datetime.utcnow().time()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Order status updated successfully',
            'data': order.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Failed to update order status: {str(e)}'
        }), 500

@orders_bp.route('/today', methods=['GET'])
@jwt_required()
def get_todays_orders():
    try:
        today = date.today()
        
        orders = Order.query.filter(Order.order_date == today).join(Customer).join(Subscription).join(Plan).all()
        
        # Group orders by status for easy overview
        orders_by_status = {
            'pending': [],
            'preparing': [],
            'prepared': [],
            'packed': [],
            'out_for_delivery': [],
            'delivered': [],
            'cancelled': []
        }
        
        total_orders = len(orders)
        total_revenue = 0
        
        for order in orders:
            order_data = order.to_dict()
            order_data['customer_name'] = f"{order.customer.first_name} {order.customer.last_name}"
            order_data['customer_phone'] = order.customer.phone_number
            order_data['customer_address'] = f"{order.customer.address_line1}, {order.customer.city}"
            order_data['plan_name'] = order.subscription.plan.name
            order_data['delivery_status'] = order.delivery.delivery_status if order.delivery else 'not_scheduled'
            
            if order.status in orders_by_status:
                orders_by_status[order.status].append(order_data)
            
            if order.total_amount:
                total_revenue += float(order.total_amount)
        
        return jsonify({
            'success': True,
            'data': {
                'date': today.isoformat(),
                'total_orders': total_orders,
                'total_revenue': total_revenue,
                'orders_by_status': orders_by_status,
                'summary': {
                    'pending': len(orders_by_status['pending']),
                    'preparing': len(orders_by_status['preparing']),
                    'prepared': len(orders_by_status['prepared']),
                    'packed': len(orders_by_status['packed']),
                    'out_for_delivery': len(orders_by_status['out_for_delivery']),
                    'delivered': len(orders_by_status['delivered']),
                    'cancelled': len(orders_by_status['cancelled'])
                }
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to retrieve today\'s orders: {str(e)}'
        }), 500

@orders_bp.route('/preparation-list', methods=['GET'])
@jwt_required()
def get_preparation_list():
    try:
        target_date = request.args.get('date', date.today().isoformat())
        target_date = datetime.strptime(target_date, '%Y-%m-%d').date()
        
        # Get all orders for the date that need preparation
        orders = Order.query.filter(
            Order.order_date == target_date,
            Order.status.in_(['pending', 'preparing'])
        ).join(Customer).join(Subscription).join(Plan).all()
        
        # Group by plan to calculate total quantities needed
        plan_summary = {}
        customer_orders = []
        
        for order in orders:
            plan = order.subscription.plan
            plan_name = plan.name
            
            if plan_name not in plan_summary:
                plan_summary[plan_name] = {
                    'total_orders': 0,
                    'rotis_needed': 0,
                    'rice_portions': 0,
                    'sabji_portions': 0,
                    'dal_kadhi_portions': 0,
                    'dessert_needed': 0,
                    'salad_portions': 0,
                    'raita_portions': 0,
                    'pickle_portions': 0
                }
            
            plan_summary[plan_name]['total_orders'] += 1
            plan_summary[plan_name]['rotis_needed'] += plan.rotis_count
            if plan.rice_included:
                plan_summary[plan_name]['rice_portions'] += 1
            plan_summary[plan_name]['sabji_portions'] += 1
            plan_summary[plan_name]['dal_kadhi_portions'] += 1
            if plan.includes_salad:
                plan_summary[plan_name]['salad_portions'] += 1
            if plan.includes_raita:
                plan_summary[plan_name]['raita_portions'] += 1
            if plan.includes_pickle:
                plan_summary[plan_name]['pickle_portions'] += 1
            
            # Add dessert if it's the right day (simplified logic)
            if plan.dessert_frequency == 'weekly' and target_date.weekday() == 4:  # Friday
                plan_summary[plan_name]['dessert_needed'] += 1
            
            customer_orders.append({
                'order_id': order.id,
                'customer_name': f"{order.customer.first_name} {order.customer.last_name}",
                'plan_name': plan_name,
                'special_requests': order.special_requests,
                'dietary_restrictions': order.customer.dietary_restrictions,
                'status': order.status
            })
        
        return jsonify({
            'success': True,
            'data': {
                'date': target_date.isoformat(),
                'total_orders': len(orders),
                'plan_summary': plan_summary,
                'customer_orders': customer_orders
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to generate preparation list: {str(e)}'
        }), 500

