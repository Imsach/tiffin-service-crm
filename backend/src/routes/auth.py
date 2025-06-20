from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
import bcrypt
from src.models.database import db, User
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({
                'success': False,
                'message': 'Username and password are required'
            }), 400
        
        user = User.query.filter_by(username=username).first()
        
        if user and bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
            # Update last login
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            access_token = create_access_token(
                identity=user.id,
                additional_claims={
                    'username': user.username,
                    'role': user.role,
                    'first_name': user.first_name,
                    'last_name': user.last_name
                }
            )
            refresh_token = create_refresh_token(identity=user.id)
            
            return jsonify({
                'success': True,
                'data': {
                    'access_token': access_token,
                    'refresh_token': refresh_token,
                    'user': user.to_dict()
                }
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Invalid username or password'
            }), 401
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Login failed: {str(e)}'
        }), 500

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({
                'success': False,
                'message': 'User not found'
            }), 404
        
        access_token = create_access_token(
            identity=user.id,
            additional_claims={
                'username': user.username,
                'role': user.role,
                'first_name': user.first_name,
                'last_name': user.last_name
            }
        )
        
        return jsonify({
            'success': True,
            'data': {
                'access_token': access_token
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Token refresh failed: {str(e)}'
        }), 500

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    # In a production environment, you would add the token to a blacklist
    return jsonify({
        'success': True,
        'message': 'Successfully logged out'
    }), 200

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        # Check if user already exists
        existing_user = User.query.filter(
            (User.username == data.get('username')) | 
            (User.email == data.get('email'))
        ).first()
        
        if existing_user:
            return jsonify({
                'success': False,
                'message': 'Username or email already exists'
            }), 400
        
        # Hash password
        password_hash = bcrypt.hashpw(
            data.get('password').encode('utf-8'), 
            bcrypt.gensalt()
        ).decode('utf-8')
        
        # Create new user
        new_user = User(
            username=data.get('username'),
            email=data.get('email'),
            password_hash=password_hash,
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            phone_number=data.get('phone_number'),
            role=data.get('role', 'staff')
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'User registered successfully',
            'data': new_user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Registration failed: {str(e)}'
        }), 500

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({
                'success': False,
                'message': 'User not found'
            }), 404
        
        return jsonify({
            'success': True,
            'data': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to get user info: {str(e)}'
        }), 500

