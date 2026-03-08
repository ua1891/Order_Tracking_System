import os
import sys
from datetime import datetime

# Add root project directory to path to allow absolute imports
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if root_path not in sys.path:
    sys.path.append(root_path)

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from database.models import db, Order, Notification, User
from backend.tcs_client import get_tracking_details, parse_tracking_summary
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
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default-dev-key-fallback')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///tracking.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Setup Scheduler (extracted to notifications module)
start_scheduler(app)

# --- Routes ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            flash("Logged in successfully.", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid username or password.", "danger")
            
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))

@app.route('/', methods=['GET', 'POST'])
@login_required
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
            
        # Fetch current status dynamically using the new TCS ENVIO Tracking API
        details = get_tracking_details(tracking_number)
        summary = parse_tracking_summary(details)
        
        new_order = Order(
            tracking_number=tracking_number,
            origin=summary.get('origin'),
            destination=summary.get('destination'),
            current_status=summary.get('current_status', 'PENDING')
        )
        db.session.add(new_order)
        db.session.commit()
        
        flash("Order tracking added successfully!", "success")
        return redirect(url_for('dashboard'))
        
    orders = Order.query.order_by(Order.last_updated.desc()).all()
    return render_template('dashboard.html', orders=orders)

@app.route('/order/<int:order_id>')
@login_required
def order_detail(order_id):
    order = Order.query.get_or_404(order_id)
    details = get_tracking_details(order.tracking_number)
    return render_template('detail.html', order=order, details=details)

@app.route('/api/notifications')
@login_required
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
        
        # Create default admin user if none exists
        if not User.query.filter_by(username='admin').first():
            print("Creating default admin user...")
            admin_user = User(username='admin')
            admin_user.set_password('admin')
            db.session.add(admin_user)
            db.session.commit()
            print("Admin user created (admin/admin).")
    
    # To prevent APScheduler from running twice in reloader
    app.run(debug=True, use_reloader=False)
