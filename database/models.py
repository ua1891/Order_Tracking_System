from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tracking_number = db.Column(db.String(50), unique=True, nullable=False)
    origin = db.Column(db.String(100), nullable=True)
    destination = db.Column(db.String(100), nullable=True)
    current_status = db.Column(db.String(100), default='PENDING', nullable=False)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    message = db.Column(db.String(255), nullable=False)
    is_read = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    order = db.relationship('Order', backref=db.backref('notifications', lazy=True))
