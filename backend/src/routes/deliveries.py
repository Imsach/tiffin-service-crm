from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models.database import db, Delivery, Order, Customer
from ..utils.route_optimizer import RouteOptimizer
from datetime import datetime, date
import json

deliveries_bp = Blueprint('deliveries', __name__)
route_optimizer = RouteOptimizer()

@deliveries_bp.route('', methods=['GET'])
@jwt_required()
def get_deliveries():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        delivery_date = request.args.get('delivery_date')
        status = request.args.get('status')
        
        query = db.session.query(
            Delivery.id,
            Delivery.delivery_date,
            Delivery.delivery_status,
            Delivery.delivery_address,
            Delivery.delivery_instructions,
            Delivery.estimated_delivery_time,
            Delivery.actual_delivery_time,
            Delivery.created_at,
            Customer.first_name.label('customer_first_name'),
            Customer.last_name.label('customer_last_name'),
            Customer.phone_number.label('customer_phone'),
            Customer.city,
            Customer.province
        ).join(Order, Delivery.order_id == Order.id)\
         .join(Customer, Order.customer_id == Customer.id)
        
        if delivery_date:
            query = query.filter(Delivery.delivery_date == delivery_date)
        if status:
            query = query.filter(Delivery.delivery_status == status)
        
        query = query.order_by(Delivery.delivery_date.desc(), Delivery.estimated_delivery_time)
        
        deliveries = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        delivery_list = []
        for delivery in deliveries.items:
            delivery_list.append({
                'id': delivery.id,
                'delivery_date': delivery.delivery_date.isoformat(),
                'delivery_status': delivery.delivery_status,
                'delivery_address': delivery.delivery_address,
                'delivery_instructions': delivery.delivery_instructions,
                'estimated_delivery_time': delivery.estimated_delivery_time.isoformat() if delivery.estimated_delivery_time else None,
                'actual_delivery_time': delivery.actual_delivery_time.isoformat() if delivery.actual_delivery_time else None,
                'customer_name': f"{delivery.customer_first_name} {delivery.customer_last_name}",
                'customer_phone': delivery.customer_phone,
                'city': delivery.city,
                'province': delivery.province,
                'created_at': delivery.created_at.isoformat()
            })
        
        return jsonify({
            'success': True,
            'data': {
                'deliveries': delivery_list,
                'pagination': {
                    'page': deliveries.page,
                    'pages': deliveries.pages,
                    'per_page': deliveries.per_page,
                    'total': deliveries.total
                }
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@deliveries_bp.route('/today', methods=['GET'])
@jwt_required()
def get_todays_deliveries():
    try:
        today = date.today()
        
        deliveries_query = db.session.query(
            Delivery.id,
            Delivery.delivery_status,
            Delivery.delivery_address,
            Delivery.delivery_instructions,
            Delivery.estimated_delivery_time,
            Customer.first_name.label('customer_first_name'),
            Customer.last_name.label('customer_last_name'),
            Customer.phone_number.label('customer_phone'),
            Customer.city,
            Customer.province
        ).join(Order, Delivery.order_id == Order.id)\
         .join(Customer, Order.customer_id == Customer.id)\
         .filter(Delivery.delivery_date == today)
        
        deliveries = deliveries_query.all()
        
        # Group by status
        status_summary = {}
        deliveries_by_zone = {}
        
        delivery_list = []
        for delivery in deliveries:
            status = delivery.delivery_status
            status_summary[status] = status_summary.get(status, 0) + 1
            
            # Group by city/zone
            zone = delivery.city or 'Unknown'
            if zone not in deliveries_by_zone:
                deliveries_by_zone[zone] = []
            
            delivery_data = {
                'id': delivery.id,
                'delivery_status': delivery.delivery_status,
                'delivery_address': delivery.delivery_address,
                'delivery_instructions': delivery.delivery_instructions,
                'estimated_delivery_time': delivery.estimated_delivery_time.isoformat() if delivery.estimated_delivery_time else None,
                'customer_name': f"{delivery.customer_first_name} {delivery.customer_last_name}",
                'customer_phone': delivery.customer_phone,
                'city': delivery.city,
                'province': delivery.province
            }
            
            delivery_list.append(delivery_data)
            deliveries_by_zone[zone].append(delivery_data)
        
        return jsonify({
            'success': True,
            'data': {
                'total_deliveries': len(deliveries),
                'summary': status_summary,
                'deliveries_by_zone': deliveries_by_zone,
                'deliveries': delivery_list
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@deliveries_bp.route('/<int:delivery_id>/status', methods=['PUT'])
@jwt_required()
def update_delivery_status(delivery_id):
    try:
        data = request.get_json()
        new_status = data.get('delivery_status')
        
        if not new_status:
            return jsonify({'success': False, 'message': 'Delivery status is required'}), 400
        
        delivery = Delivery.query.get_or_404(delivery_id)
        delivery.delivery_status = new_status
        
        if new_status == 'delivered':
            delivery.actual_delivery_time = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Delivery status updated successfully',
            'data': {
                'id': delivery.id,
                'delivery_status': delivery.delivery_status,
                'actual_delivery_time': delivery.actual_delivery_time.isoformat() if delivery.actual_delivery_time else None
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@deliveries_bp.route('/optimize-route', methods=['POST'])
@jwt_required()
def optimize_delivery_route():
    try:
        data = request.get_json()
        delivery_date = data.get('delivery_date', date.today().isoformat())
        start_location = data.get('start_location', {
            'latitude': 49.1042,
            'longitude': -122.6604,
            'address': 'Langley, BC, Canada'
        })
        
        # Parse delivery date
        if isinstance(delivery_date, str):
            delivery_date = datetime.strptime(delivery_date, '%Y-%m-%d').date()
        
        # Get deliveries for the specified date
        deliveries_query = db.session.query(
            Delivery.id,
            Delivery.delivery_address,
            Delivery.delivery_instructions,
            Delivery.estimated_delivery_time,
            Customer.first_name.label('customer_first_name'),
            Customer.last_name.label('customer_last_name'),
            Customer.phone_number.label('customer_phone'),
            Customer.city,
            Customer.province
        ).join(Order, Delivery.order_id == Order.id)\
         .join(Customer, Order.customer_id == Customer.id)\
         .filter(Delivery.delivery_date == delivery_date)\
         .filter(Delivery.delivery_status.in_(['scheduled', 'in_transit']))
        
        deliveries = deliveries_query.all()
        
        if not deliveries:
            return jsonify({
                'success': True,
                'data': {
                    'optimized_route': [],
                    'total_distance_km': 0,
                    'estimated_duration': '0h 0m',
                    'total_deliveries': 0,
                    'message': 'No deliveries found for optimization'
                }
            })
        
        # Convert to list of dictionaries for the optimizer
        delivery_list = []
        for delivery in deliveries:
            delivery_list.append({
                'id': delivery.id,
                'delivery_address': delivery.delivery_address,
                'delivery_instructions': delivery.delivery_instructions,
                'customer_name': f"{delivery.customer_first_name} {delivery.customer_last_name}",
                'customer_phone': delivery.customer_phone,
                'city': delivery.city,
                'province': delivery.province
            })
        
        # Optimize the route
        optimized_result = route_optimizer.optimize_delivery_route(delivery_list, start_location)
        
        # Update delivery sequence in database
        for route_item in optimized_result['optimized_route']:
            delivery = Delivery.query.get(route_item['delivery_id'])
            if delivery:
                # Update estimated delivery time based on optimized sequence
                estimated_time = datetime.strptime(route_item['estimated_time'], '%H:%M').time()
                delivery.estimated_delivery_time = datetime.combine(delivery_date, estimated_time)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': optimized_result
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@deliveries_bp.route('/bulk-assign', methods=['POST'])
@jwt_required()
def bulk_assign_deliveries():
    try:
        data = request.get_json()
        delivery_ids = data.get('delivery_ids', [])
        driver_id = data.get('driver_id')
        vehicle_id = data.get('vehicle_id')
        
        if not delivery_ids:
            return jsonify({'success': False, 'message': 'No delivery IDs provided'}), 400
        
        updated_count = 0
        for delivery_id in delivery_ids:
            delivery = Delivery.query.get(delivery_id)
            if delivery:
                if driver_id:
                    delivery.driver_id = driver_id
                if vehicle_id:
                    delivery.vehicle_id = vehicle_id
                updated_count += 1
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Successfully assigned {updated_count} deliveries',
            'data': {'updated_count': updated_count}
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@deliveries_bp.route('/zones', methods=['GET'])
@jwt_required()
def get_delivery_zones():
    try:
        delivery_date = request.args.get('delivery_date', date.today().isoformat())
        
        if isinstance(delivery_date, str):
            delivery_date = datetime.strptime(delivery_date, '%Y-%m-%d').date()
        
        zones_query = db.session.query(
            Customer.city,
            db.func.count(Delivery.id).label('delivery_count')
        ).join(Order, Delivery.order_id == Order.id)\
         .join(Customer, Order.customer_id == Customer.id)\
         .filter(Delivery.delivery_date == delivery_date)\
         .group_by(Customer.city)
        
        zones = zones_query.all()
        
        zone_data = []
        for zone in zones:
            zone_data.append({
                'zone': zone.city or 'Unknown',
                'delivery_count': zone.delivery_count
            })
        
        return jsonify({
            'success': True,
            'data': {'zones': zone_data}
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

