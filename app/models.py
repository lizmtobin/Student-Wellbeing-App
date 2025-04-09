from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
from flask_login import UserMixin
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum

class UserRole(Enum):
    STUDENT = 'student'
    COUNSELLOR = 'counsellor'
    WELLBEING_STAFF = 'wellbeing_staff'
    ADMIN = 'admin'

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    last_login = db.Column(db.DateTime)
    type = db.Column(db.String(50))
    __mapper_args__ = {
        'polymorphic_identity': 'user',
        'polymorphic_on': type
    }

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def update_last_login(self):
        self.last_login = datetime.now(timezone.utc)
        db.session.commit()

    def __repr__(self):
        return f'<User {self.username}>'

class Student(User):
    __tablename__ = 'students'
    id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    student_id = db.Column(db.String(20), unique=True)
    course = db.Column(db.String(100))
    year_of_study = db.Column(db.Integer)
    __mapper_args__ = {'polymorphic_identity': 'student'}

    def __repr__(self):
        return f'<Student {self.username}>'

class Counsellor(User):
    __tablename__ = 'counsellors'
    id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    specialization = db.Column(db.String(100))
    availability = db.Column(db.String(200))
    __mapper_args__ = {'polymorphic_identity': 'counsellor'}

    def __repr__(self):
        return f'<Counsellor {self.username}>'

class WellbeingStaff(User):
    __tablename__ = 'wellbeing_staff'
    id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    department = db.Column(db.String(100))
    role = db.Column(db.String(100))
    __mapper_args__ = {'polymorphic_identity': 'wellbeing_staff'}

    def __repr__(self):
        return f'<WellbeingStaff {self.username}>'

class Admin(User):
    __tablename__ = 'admins'
    id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    __mapper_args__ = {'polymorphic_identity': 'admin'}

    def __repr__(self):
        return f'<Admin {self.username}>'

@login.user_loader
def load_user(id):
    return User.query.get(int(id))