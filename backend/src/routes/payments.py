from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from src.models.database import db, Payment, Customer, Subscription
from datetime import datetime, date

payments_bp = Blueprint('payments', __name__)

@payments_bp.route('', methods=['GET'])
@jwt_required()
def get_payments():
    try:
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 20, type=int)
        customer_id = request.args.get('customer_id', type=int)
        payment_type = request.args.get('payment_type')
        payment_status = request.args.get('payment_status')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        query = Payment.query
        
        if customer_id:
            query = query.filter(Payment.customer_id == customer_id)
        
        if payment_type:
            query = query.filter(Payment.payment_type == payment_type)
        
        if payment_status:
            query = query.filter(Payment.payment_status == payment_status)
        
        if start_date:
            query = query.filter(Payment.payment_date >= datetime.strptime(start_date, '%Y-%m-%d'))
        
        if end_date:
            query = query.filter(Payment.payment_date <= datetime.strptime(end_date, '%Y-%m-%d'))
        
        # Join with customer for additional info
        query = query.join(Customer)
        
        payments = query.order_by(Payment.payment_date.desc()).paginate(
            page=page, 
            per_page=limit, 
            error_out=False
        )
        
        result = []
        for payment in payments.items:
            payment_data = payment.to_dict()
            payment_data['customer_name'] = f"{payment.customer.first_name} {payment.customer.last_name}"
            payment_data['customer_phone'] = payment.customer.phone_number
            result.append(payment_data)
        
        return jsonify({
            'success': True,
            'data': {
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

@payments_bp.route('', methods=['POST'])
@jwt_required()
def create_payment():
    try:
        data = request.get_json()
        
        # Validate customer exists
        customer = Customer.query.get(data.get('customer_id'))
        if not customer:
            return jsonify({
                'success': False,
                'message': 'Customer not found'
            }), 404
        
        # Validate subscription if provided
        subscription_id = data.get('subscription_id')
        if subscription_id:
            subscription = Subscription.query.get(subscription_id)
            if not subscription or subscription.customer_id != customer.id:
                return jsonify({
                    'success': False,
                    'message': 'Invalid subscription for this customer'
                }), 400
        
        new_payment = Payment(
            customer_id=data.get('customer_id'),
            subscription_id=subscription_id,
            amount=data.get('amount'),
            payment_type=data.get('payment_type'),
            payment_method=data.get('payment_method'),
            transaction_id=data.get('transaction_id'),
            payment_status=data.get('payment_status', 'completed'),
            description=data.get('description')
        )
        
        db.session.add(new_payment)
        
        # Update customer balance if it's a balance addition
        if data.get('payment_type') == 'balance_addition':
            customer.account_balance = float(customer.account_balance) + float(data.get('amount'))
        elif data.get('payment_type') == 'subscription':
            # Deduct from customer balance if paying from account balance
            if data.get('payment_method') == 'account_balance':
                if float(customer.account_balance) < float(data.get('amount')):
                    return jsonify({
                        'success': False,
                        'message': 'Insufficient account balance'
                    }), 400
                customer.account_balance = float(customer.account_balance) - float(data.get('amount'))
        
        customer.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Payment recorded successfully',
            'data': new_payment.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Failed to create payment: {str(e)}'
        }), 500

@payments_bp.route('/<int:payment_id>', methods=['GET'])
@jwt_required()
def get_payment(payment_id):
    try:
        payment = Payment.query.get(payment_id)
        
        if not payment:
            return jsonify({
                'success': False,
                'message': 'Payment not found'
            }), 404
        
        # Get payment with related data
        payment_data = payment.to_dict()
        payment_data['customer'] = payment.customer.to_dict()
        if payment.subscription:
            payment_data['subscription'] = payment.subscription.to_dict()
        
        return jsonify({
            'success': True,
            'data': payment_data
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to retrieve payment: {str(e)}'
        }), 500

@payments_bp.route('/<int:payment_id>', methods=['PUT'])
@jwt_required()
def update_payment(payment_id):
    try:
        payment = Payment.query.get(payment_id)
        
        if not payment:
            return jsonify({
                'success': False,
                'message': 'Payment not found'
            }), 404
        
        data = request.get_json()
        
        # Update payment fields
        for field in ['payment_status', 'transaction_id', 'description']:
            if field in data:
                setattr(payment, field, data[field])
        
        payment.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Payment updated successfully',
            'data': payment.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Failed to update payment: {str(e)}'
        }), 500

@payments_bp.route('/summary', methods=['GET'])
@jwt_required()
def get_payment_summary():
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Default to current month if no dates provided
        if not start_date or not end_date:
            today = date.today()
            start_date = today.replace(day=1).isoformat()
            end_date = today.isoformat()
        
        start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
        end_datetime = datetime.strptime(end_date, '%Y-%m-%d')
        end_datetime = end_datetime.replace(hour=23, minute=59, second=59)
        
        # Get payments in date range
        payments = Payment.query.filter(
            Payment.payment_date >= start_datetime,
            Payment.payment_date <= end_datetime,
            Payment.payment_status == 'completed'
        ).all()
        
        # Calculate summary statistics
        total_revenue = sum(float(p.amount) for p in payments)
        total_transactions = len(payments)
        
        # Group by payment type
        by_payment_type = {}
        for payment in payments:
            payment_type = payment.payment_type
            if payment_type not in by_payment_type:
                by_payment_type[payment_type] = {
                    'count': 0,
                    'total_amount': 0
                }
            by_payment_type[payment_type]['count'] += 1
            by_payment_type[payment_type]['total_amount'] += float(payment.amount)
        
        # Group by payment method
        by_payment_method = {}
        for payment in payments:
            payment_method = payment.payment_method
            if payment_method not in by_payment_method:
                by_payment_method[payment_method] = {
                    'count': 0,
                    'total_amount': 0
                }
            by_payment_method[payment_method]['count'] += 1
            by_payment_method[payment_method]['total_amount'] += float(payment.amount)
        
        # Daily breakdown
        daily_breakdown = {}
        for payment in payments:
            payment_date = payment.payment_date.date().isoformat()
            if payment_date not in daily_breakdown:
                daily_breakdown[payment_date] = {
                    'count': 0,
                    'total_amount': 0
                }
            daily_breakdown[payment_date]['count'] += 1
            daily_breakdown[payment_date]['total_amount'] += float(payment.amount)
        
        return jsonify({
            'success': True,
            'data': {
                'period': {
                    'start_date': start_date,
                    'end_date': end_date
                },
                'summary': {
                    'total_revenue': total_revenue,
                    'total_transactions': total_transactions,
                    'average_transaction': total_revenue / total_transactions if total_transactions > 0 else 0
                },
                'by_payment_type': by_payment_type,
                'by_payment_method': by_payment_method,
                'daily_breakdown': daily_breakdown
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to generate payment summary: {str(e)}'
        }), 500

@payments_bp.route('/process-subscription-billing', methods=['POST'])
@jwt_required()
def process_subscription_billing():
    try:
        data = request.get_json()
        billing_date = data.get('billing_date', date.today().isoformat())
        billing_date = datetime.strptime(billing_date, '%Y-%m-%d').date()
        
        # Get subscriptions due for billing
        due_subscriptions = Subscription.query.filter(
            Subscription.status == 'active',
            Subscription.next_billing_date <= billing_date,
            Subscription.auto_renew == True
        ).join(Customer).all()
        
        processed_payments = []
        failed_payments = []
        
        for subscription in due_subscriptions:
            try:
                customer = subscription.customer
                plan = subscription.plan
                
                # Check if customer has sufficient balance
                if float(customer.account_balance) >= float(plan.price):
                    # Process payment from account balance
                    payment = Payment(
                        customer_id=customer.id,
                        subscription_id=subscription.id,
                        amount=plan.price,
                        payment_type='subscription',
                        payment_method='account_balance',
                        payment_status='completed',
                        description=f'Auto-billing for {plan.name} - {billing_date}'
                    )
                    
                    # Deduct from customer balance
                    customer.account_balance = float(customer.account_balance) - float(plan.price)
                    
                    # Update next billing date
                    if subscription.billing_cycle == 'monthly':
                        subscription.next_billing_date = billing_date + timedelta(days=30)
                    elif subscription.billing_cycle == 'weekly':
                        subscription.next_billing_date = billing_date + timedelta(days=7)
                    
                    db.session.add(payment)
                    processed_payments.append({
                        'customer_id': customer.id,
                        'customer_name': f"{customer.first_name} {customer.last_name}",
                        'amount': float(plan.price),
                        'payment_id': payment.id
                    })
                    
                else:
                    # Insufficient balance
                    failed_payments.append({
                        'customer_id': customer.id,
                        'customer_name': f"{customer.first_name} {customer.last_name}",
                        'required_amount': float(plan.price),
                        'current_balance': float(customer.account_balance),
                        'reason': 'Insufficient balance'
                    })
                    
            except Exception as e:
                failed_payments.append({
                    'customer_id': subscription.customer_id,
                    'customer_name': f"{subscription.customer.first_name} {subscription.customer.last_name}",
                    'reason': f'Processing error: {str(e)}'
                })
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Processed {len(processed_payments)} payments, {len(failed_payments)} failed',
            'data': {
                'billing_date': billing_date.isoformat(),
                'processed_payments': processed_payments,
                'failed_payments': failed_payments,
                'total_processed': len(processed_payments),
                'total_failed': len(failed_payments),
                'total_revenue': sum(p['amount'] for p in processed_payments)
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Failed to process subscription billing: {str(e)}'
        }), 500

