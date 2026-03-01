import os
import sys
from datetime import datetime

# Add root project directory to path to allow absolute imports
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if root_path not in sys.path:
    sys.path.append(root_path)

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from database.models import db, Order, Notification
from backend.tcs_client import get_tracking_details
from notifications.scheduler import start_scheduler

# Define paths for frontend and database based on new structure
frontend_templates_path = os.path.join(root_path, 'frontend', 'templates')
frontend_static_path = os.path.join(root_path, 'frontend', 'static')
database_instance_path = os.path.join(root_path, 'database', 'instance')

app = Flask(__name__, 
            template_folder=frontend_templates_path, 
            static_folder=frontend_static_path,
            instance_path=database_instance_path)

# Basic config
app.config['SECRET_KEY'] = 'super-secret-key-123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tracking.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Setup Scheduler (extracted to notifications module)
start_scheduler(app)

# --- Routes ---

@app.route('/', methods=['GET', 'POST'])
def dashboard():
    if request.method == 'POST':
        tracking_number = request.form.get('tracking_number')
        
        if not tracking_number:
            flash("Tracking Number is required.", "danger")
            return redirect(url_for('dashboard'))
            
        existing = Order.query.filter_by(tracking_number=tracking_number).first()
        if existing:
            flash("Tracking Number already exists in the system.", "warning")
            return redirect(url_for('dashboard'))
            
        # Optionally fetch current status dynamically
        details = get_tracking_details(tracking_number)
        current_status = "PENDING"
        origin = None
        destination = None
        
        if details:
            if 'Checkpoints' in details and len(details['Checkpoints']) > 0:
                 current_status = details['Checkpoints'][-1].get('status', 'PENDING')
            
            if 'TrackInfo' in details and len(details['TrackInfo']) > 0:
                track_info = details['TrackInfo'][0]
                origin_city = track_info.get('origin', '')
                origin_country = track_info.get('originCountry', '')
                dest_city = track_info.get('destination', '')
                dest_country = track_info.get('destinationCountry', '')
                
                origin = f"{origin_city}, {origin_country}".strip(', ')
                destination = f"{dest_city}, {dest_country}".strip(', ')
        
        new_order = Order(
            tracking_number=tracking_number,
            origin=origin,
            destination=destination,
            current_status=current_status
        )
        db.session.add(new_order)
        db.session.commit()
        
        flash("Order tracking added successfully!", "success")
        return redirect(url_for('dashboard'))
        
    orders = Order.query.order_by(Order.last_updated.desc()).all()
    return render_template('dashboard.html', orders=orders)

@app.route('/order/<int:order_id>')
def order_detail(order_id):
    order = Order.query.get_or_404(order_id)
    details = get_tracking_details(order.tracking_number)
    return render_template('detail.html', order=order, details=details)

@app.route('/api/notifications')
def get_notifications():
    """API endpoint for frontend to poll unread notifications."""
    unreads = Notification.query.filter_by(is_read=False).all()
    results = []
    for n in unreads:
        results.append({
            'id': n.id,
            'message': n.message,
            'tracking_number': n.order.tracking_number,
            'created_at': n.created_at.strftime('%Y-%m-%d %H:%M:%S')
        })
        n.is_read = True
    
    db.session.commit()
    return jsonify(results)

if __name__ == '__main__':
    with app.app_context():
        # Ensure the instance folder exists
        os.makedirs(database_instance_path, exist_ok=True)
        db.create_all()
    
    # To prevent APScheduler from running twice in reloader
    app.run(debug=True, use_reloader=False)
