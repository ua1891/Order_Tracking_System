import os
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from database.models import db, Order, Notification
from backend.tcs_client import get_tracking_details

def check_tracking_updates(app):
    """Polls TCS API for all active orders and updates status if changed."""
    # We need an application context to interact with the database
    with app.app_context():
        # Fetch all active orders
        active_orders = Order.query.filter(~Order.current_status.in_(['DELIVERED', 'RETURNED', 'CANCELLED'])).all()
        for order in active_orders:
            details = get_tracking_details(order.tracking_number)
            if details and 'Checkpoints' in details and len(details['Checkpoints']) > 0:
                checkpoints = details.get('Checkpoints', [])
                # Taking the last checkpoint as latest status
                latest_checkpoint = checkpoints[-1]
                new_status = latest_checkpoint.get('status')
                
                if new_status and new_status != order.current_status:
                    # Status changed
                    order.current_status = new_status
                    order.last_updated = datetime.utcnow()
                    
                    # Create Notification
                    notif = Notification(
                        order_id=order.id,
                        message=f"Order {order.tracking_number} status changed to {new_status}"
                    )
                    db.session.add(notif)
                    
        db.session.commit()

def start_scheduler(app):
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=check_tracking_updates, args=[app], trigger="interval", minutes=30)
    scheduler.start()
