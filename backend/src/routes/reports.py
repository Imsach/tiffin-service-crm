from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from src.models.database import db, Order, Customer, Subscription, Payment, Delivery, Expense
from datetime import datetime, date, timedelta
from sqlalchemy import func

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/daily-summary', methods=['GET'])
@jwt_required()
def get_daily_summary():
    try:
        report_date = request.args.get('date', date.today().isoformat())
        report_date = datetime.strptime(report_date, '%Y-%m-%d').date()
        
        # Get orders for the date
        orders = Order.query.filter(Order.order_date == report_date).all()
        total_orders = len(orders)
        
        # Get deliveries for the date
        deliveries = Delivery.query.filter(Delivery.delivery_date == report_date).all()
        total_deliveries = len(deliveries)
        completed_deliveries = len([d for d in deliveries if d.delivery_status == 'delivered'])
        
        # Get payments for the date
        start_datetime = datetime.combine(report_date, datetime.min.time())
        end_datetime = datetime.combine(report_date, datetime.max.time())
        
        payments = Payment.query.filter(
            Payment.payment_date >= start_datetime,
            Payment.payment_date <= end_datetime,
            Payment.payment_status == 'completed'
        ).all()
        
        total_revenue = sum(float(p.amount) for p in payments)
        
        # Get expenses for the date
        expenses = Expense.query.filter(Expense.expense_date == report_date).all()
        total_expenses = sum(float(e.amount) for e in expenses)
        
        # Calculate profit
        profit = total_revenue - total_expenses
        
        # Get active customers count
        active_customers = Customer.query.filter(Customer.status == 'active').count()
        
        # Get new customers for the date
        new_customers = Customer.query.filter(
            func.date(Customer.created_at) == report_date
        ).count()
        
        # Order status breakdown
        order_status_breakdown = {}
        for order in orders:
            status = order.status
            if status not in order_status_breakdown:
                order_status_breakdown[status] = 0
            order_status_breakdown[status] += 1
        
        # Delivery status breakdown
        delivery_status_breakdown = {}
        for delivery in deliveries:
            status = delivery.delivery_status
            if status not in delivery_status_breakdown:
                delivery_status_breakdown[status] = 0
            delivery_status_breakdown[status] += 1
        
        return jsonify({
            'success': True,
            'data': {
                'date': report_date.isoformat(),
                'summary': {
                    'total_orders': total_orders,
                    'total_deliveries': total_deliveries,
                    'completed_deliveries': completed_deliveries,
                    'delivery_completion_rate': (completed_deliveries / total_deliveries * 100) if total_deliveries > 0 else 0,
                    'total_revenue': total_revenue,
                    'total_expenses': total_expenses,
                    'profit': profit,
                    'active_customers': active_customers,
                    'new_customers': new_customers
                },
                'order_status_breakdown': order_status_breakdown,
                'delivery_status_breakdown': delivery_status_breakdown,
                'revenue_breakdown': {
                    'subscription_payments': sum(float(p.amount) for p in payments if p.payment_type == 'subscription'),
                    'balance_additions': sum(float(p.amount) for p in payments if p.payment_type == 'balance_addition'),
                    'other_payments': sum(float(p.amount) for p in payments if p.payment_type not in ['subscription', 'balance_addition'])
                }
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to generate daily summary: {str(e)}'
        }), 500

@reports_bp.route('/monthly-summary', methods=['GET'])
@jwt_required()
def get_monthly_summary():
    try:
        year = request.args.get('year', date.today().year, type=int)
        month = request.args.get('month', date.today().month, type=int)
        
        # Calculate date range for the month
        start_date = date(year, month, 1)
        if month == 12:
            end_date = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = date(year, month + 1, 1) - timedelta(days=1)
        
        start_datetime = datetime.combine(start_date, datetime.min.time())
        end_datetime = datetime.combine(end_date, datetime.max.time())
        
        # Get orders for the month
        orders = Order.query.filter(
            Order.order_date >= start_date,
            Order.order_date <= end_date
        ).all()
        
        # Get payments for the month
        payments = Payment.query.filter(
            Payment.payment_date >= start_datetime,
            Payment.payment_date <= end_datetime,
            Payment.payment_status == 'completed'
        ).all()
        
        # Get expenses for the month
        expenses = Expense.query.filter(
            Expense.expense_date >= start_date,
            Expense.expense_date <= end_date
        ).all()
        
        # Calculate totals
        total_orders = len(orders)
        total_revenue = sum(float(p.amount) for p in payments)
        total_expenses = sum(float(e.amount) for e in expenses)
        profit = total_revenue - total_expenses
        
        # Get customer statistics
        customers_at_start = Customer.query.filter(
            Customer.created_at < start_datetime,
            Customer.status == 'active'
        ).count()
        
        new_customers = Customer.query.filter(
            Customer.created_at >= start_datetime,
            Customer.created_at <= end_datetime
        ).count()
        
        active_customers = Customer.query.filter(Customer.status == 'active').count()
        
        # Daily breakdown
        daily_stats = {}
        current_date = start_date
        while current_date <= end_date:
            daily_orders = [o for o in orders if o.order_date == current_date]
            daily_payments = [p for p in payments if p.payment_date.date() == current_date]
            daily_expenses = [e for e in expenses if e.expense_date == current_date]
            
            daily_stats[current_date.isoformat()] = {
                'orders': len(daily_orders),
                'revenue': sum(float(p.amount) for p in daily_payments),
                'expenses': sum(float(e.amount) for e in daily_expenses),
                'profit': sum(float(p.amount) for p in daily_payments) - sum(float(e.amount) for e in daily_expenses)
            }
            
            current_date += timedelta(days=1)
        
        # Top customers by orders
        customer_order_counts = {}
        for order in orders:
            customer_id = order.customer_id
            if customer_id not in customer_order_counts:
                customer_order_counts[customer_id] = {
                    'customer': order.customer,
                    'order_count': 0,
                    'total_amount': 0
                }
            customer_order_counts[customer_id]['order_count'] += 1
            if order.total_amount:
                customer_order_counts[customer_id]['total_amount'] += float(order.total_amount)
        
        top_customers = sorted(
            customer_order_counts.values(),
            key=lambda x: x['order_count'],
            reverse=True
        )[:10]
        
        top_customers_data = []
        for customer_data in top_customers:
            customer = customer_data['customer']
            top_customers_data.append({
                'customer_id': customer.id,
                'customer_name': f"{customer.first_name} {customer.last_name}",
                'order_count': customer_data['order_count'],
                'total_amount': customer_data['total_amount']
            })
        
        return jsonify({
            'success': True,
            'data': {
                'period': {
                    'year': year,
                    'month': month,
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat()
                },
                'summary': {
                    'total_orders': total_orders,
                    'total_revenue': total_revenue,
                    'total_expenses': total_expenses,
                    'profit': profit,
                    'profit_margin': (profit / total_revenue * 100) if total_revenue > 0 else 0,
                    'customers_at_start': customers_at_start,
                    'new_customers': new_customers,
                    'active_customers': active_customers,
                    'average_daily_orders': total_orders / (end_date - start_date).days if (end_date - start_date).days > 0 else 0,
                    'average_order_value': total_revenue / total_orders if total_orders > 0 else 0
                },
                'daily_breakdown': daily_stats,
                'top_customers': top_customers_data
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to generate monthly summary: {str(e)}'
        }), 500

@reports_bp.route('/customer-activity', methods=['GET'])
@jwt_required()
def get_customer_activity():
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Default to last 30 days if no dates provided
        if not start_date or not end_date:
            end_date = date.today()
            start_date = end_date - timedelta(days=30)
        else:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        # Get all customers with their activity
        customers = Customer.query.all()
        customer_activity = []
        
        for customer in customers:
            # Get orders in date range
            customer_orders = Order.query.filter(
                Order.customer_id == customer.id,
                Order.order_date >= start_date,
                Order.order_date <= end_date
            ).all()
            
            # Get payments in date range
            start_datetime = datetime.combine(start_date, datetime.min.time())
            end_datetime = datetime.combine(end_date, datetime.max.time())
            
            customer_payments = Payment.query.filter(
                Payment.customer_id == customer.id,
                Payment.payment_date >= start_datetime,
                Payment.payment_date <= end_datetime,
                Payment.payment_status == 'completed'
            ).all()
            
            # Get active subscriptions
            active_subscriptions = Subscription.query.filter(
                Subscription.customer_id == customer.id,
                Subscription.status == 'active'
            ).count()
            
            # Calculate last order date
            last_order = Order.query.filter(Order.customer_id == customer.id).order_by(Order.order_date.desc()).first()
            last_order_date = last_order.order_date if last_order else None
            
            # Calculate activity score (orders + payments in period)
            activity_score = len(customer_orders) + len(customer_payments)
            
            customer_activity.append({
                'customer_id': customer.id,
                'customer_name': f"{customer.first_name} {customer.last_name}",
                'customer_phone': customer.phone_number,
                'customer_email': customer.email,
                'status': customer.status,
                'account_balance': float(customer.account_balance),
                'orders_in_period': len(customer_orders),
                'payments_in_period': len(customer_payments),
                'total_paid_in_period': sum(float(p.amount) for p in customer_payments),
                'active_subscriptions': active_subscriptions,
                'last_order_date': last_order_date.isoformat() if last_order_date else None,
                'activity_score': activity_score,
                'created_at': customer.created_at.isoformat() if customer.created_at else None
            })
        
        # Sort by activity score
        customer_activity.sort(key=lambda x: x['activity_score'], reverse=True)
        
        # Calculate summary statistics
        total_customers = len(customers)
        active_customers = len([c for c in customer_activity if c['status'] == 'active'])
        customers_with_orders = len([c for c in customer_activity if c['orders_in_period'] > 0])
        customers_with_payments = len([c for c in customer_activity if c['payments_in_period'] > 0])
        
        return jsonify({
            'success': True,
            'data': {
                'period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat()
                },
                'summary': {
                    'total_customers': total_customers,
                    'active_customers': active_customers,
                    'customers_with_orders': customers_with_orders,
                    'customers_with_payments': customers_with_payments,
                    'customer_retention_rate': (customers_with_orders / active_customers * 100) if active_customers > 0 else 0
                },
                'customer_activity': customer_activity
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to generate customer activity report: {str(e)}'
        }), 500

@reports_bp.route('/financial-summary', methods=['GET'])
@jwt_required()
def get_financial_summary():
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Default to current month if no dates provided
        if not start_date or not end_date:
            today = date.today()
            start_date = today.replace(day=1)
            end_date = today
        else:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        start_datetime = datetime.combine(start_date, datetime.min.time())
        end_datetime = datetime.combine(end_date, datetime.max.time())
        
        # Get payments
        payments = Payment.query.filter(
            Payment.payment_date >= start_datetime,
            Payment.payment_date <= end_datetime,
            Payment.payment_status == 'completed'
        ).all()
        
        # Get expenses
        expenses = Expense.query.filter(
            Expense.expense_date >= start_date,
            Expense.expense_date <= end_date
        ).all()
        
        # Calculate revenue breakdown
        revenue_by_type = {}
        for payment in payments:
            payment_type = payment.payment_type
            if payment_type not in revenue_by_type:
                revenue_by_type[payment_type] = 0
            revenue_by_type[payment_type] += float(payment.amount)
        
        # Calculate expense breakdown
        expenses_by_category = {}
        for expense in expenses:
            category = expense.category
            if category not in expenses_by_category:
                expenses_by_category[category] = 0
            expenses_by_category[category] += float(expense.amount)
        
        total_revenue = sum(revenue_by_type.values())
        total_expenses = sum(expenses_by_category.values())
        net_profit = total_revenue - total_expenses
        
        # Calculate outstanding balances
        customers_with_negative_balance = Customer.query.filter(Customer.account_balance < 0).all()
        total_outstanding = sum(abs(float(c.account_balance)) for c in customers_with_negative_balance)
        
        # Calculate total customer balances (positive)
        customers_with_positive_balance = Customer.query.filter(Customer.account_balance > 0).all()
        total_prepaid = sum(float(c.account_balance) for c in customers_with_positive_balance)
        
        return jsonify({
            'success': True,
            'data': {
                'period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat()
                },
                'revenue': {
                    'total_revenue': total_revenue,
                    'by_type': revenue_by_type
                },
                'expenses': {
                    'total_expenses': total_expenses,
                    'by_category': expenses_by_category
                },
                'profit': {
                    'net_profit': net_profit,
                    'profit_margin': (net_profit / total_revenue * 100) if total_revenue > 0 else 0
                },
                'balances': {
                    'total_outstanding': total_outstanding,
                    'total_prepaid': total_prepaid,
                    'net_balance': total_prepaid - total_outstanding
                },
                'transactions': {
                    'total_payments': len(payments),
                    'total_expenses': len(expenses),
                    'average_payment': total_revenue / len(payments) if len(payments) > 0 else 0,
                    'average_expense': total_expenses / len(expenses) if len(expenses) > 0 else 0
                }
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to generate financial summary: {str(e)}'
        }), 500

