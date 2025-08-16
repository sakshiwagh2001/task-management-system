from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Position(db.Model):  
    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(20), nullable=False)  
    users = db.relationship('User', backref='position', lazy=True)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(500), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('position.id'), nullable=False)
    created_tasks = db.relationship('Task', foreign_keys='Task.created_by', backref='creator', lazy=True)
    assigned_tasks = db.relationship('Task', foreign_keys='Task.assigned_to', backref='assignee', lazy=True)
    approved_tasks = db.relationship('Task', foreign_keys='Task.approved_by', backref='approver', lazy=True)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    deadline = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default="Pending")  
    remark = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    assigned_to = db.Column(db.Integer, db.ForeignKey('user.id'))
    approved_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
