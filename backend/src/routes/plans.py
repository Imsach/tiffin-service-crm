from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from src.models.database import db, Plan

plans_bp = Blueprint('plans', __name__)

@plans_bp.route('', methods=['GET'])
def get_plans():
    try:
        status = request.args.get('status', 'active')
        is_trial = request.args.get('is_trial')
        
        query = Plan.query
        
        if status:
            query = query.filter(Plan.status == status)
        
        if is_trial is not None:
            is_trial_bool = is_trial.lower() == 'true'
            query = query.filter(Plan.is_trial == is_trial_bool)
        
        plans = query.order_by(Plan.price).all()
        
        return jsonify({
            'success': True,
            'data': [plan.to_dict() for plan in plans]
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to retrieve plans: {str(e)}'
        }), 500

@plans_bp.route('', methods=['POST'])
@jwt_required()
def create_plan():
    try:
        data = request.get_json()
        
        new_plan = Plan(
            name=data.get('name'),
            description=data.get('description'),
            price=data.get('price'),
            duration_days=data.get('duration_days'),
            meals_per_week=data.get('meals_per_week'),
            rotis_count=data.get('rotis_count'),
            rice_included=data.get('rice_included', True),
            sabji_size_oz=data.get('sabji_size_oz'),
            dal_kadhi_size_oz=data.get('dal_kadhi_size_oz'),
            dessert_frequency=data.get('dessert_frequency'),
            includes_paan=data.get('includes_paan', False),
            includes_salad=data.get('includes_salad', True),
            includes_raita=data.get('includes_raita', True),
            includes_pickle=data.get('includes_pickle', True),
            delivery_days=data.get('delivery_days'),
            is_trial=data.get('is_trial', False),
            requires_student_id=data.get('requires_student_id', False)
        )
        
        db.session.add(new_plan)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Plan created successfully',
            'data': new_plan.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Failed to create plan: {str(e)}'
        }), 500

@plans_bp.route('/<int:plan_id>', methods=['GET'])
def get_plan(plan_id):
    try:
        plan = Plan.query.get(plan_id)
        
        if not plan:
            return jsonify({
                'success': False,
                'message': 'Plan not found'
            }), 404
        
        return jsonify({
            'success': True,
            'data': plan.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to retrieve plan: {str(e)}'
        }), 500

@plans_bp.route('/<int:plan_id>', methods=['PUT'])
@jwt_required()
def update_plan(plan_id):
    try:
        plan = Plan.query.get(plan_id)
        
        if not plan:
            return jsonify({
                'success': False,
                'message': 'Plan not found'
            }), 404
        
        data = request.get_json()
        
        # Update plan fields
        for field in ['name', 'description', 'price', 'duration_days', 'meals_per_week',
                     'rotis_count', 'rice_included', 'sabji_size_oz', 'dal_kadhi_size_oz',
                     'dessert_frequency', 'includes_paan', 'includes_salad', 'includes_raita',
                     'includes_pickle', 'delivery_days', 'is_trial', 'requires_student_id', 'status']:
            if field in data:
                setattr(plan, field, data[field])
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Plan updated successfully',
            'data': plan.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Failed to update plan: {str(e)}'
        }), 500

@plans_bp.route('/initialize-default', methods=['POST'])
@jwt_required()
def initialize_default_plans():
    try:
        # Check if plans already exist
        existing_plans = Plan.query.count()
        if existing_plans > 0:
            return jsonify({
                'success': False,
                'message': 'Plans already exist in the system'
            }), 400
        
        # Create default plans based on Vedic Kitchen
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
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Successfully created {len(default_plans)} default plans',
            'data': [plan.to_dict() for plan in Plan.query.all()]
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Failed to initialize default plans: {str(e)}'
        }), 500

