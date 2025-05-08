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


# Define user roles as an enumeration for type safety and consistency
class UserRole(Enum):
    STUDENT = 'student'
    COUNSELLOR = 'counsellor'
    WELLBEING_STAFF = 'wellbeing_staff'
    ADMIN = 'admin'

# Base User model that implements Flask-Login's UserMixin
# This provides default implementations for user authentication methods
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

    # Password handling methods - Future proofing
    def set_password(self, password):
        """Hash and set the user's password"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verify the user's password"""
        return check_password_hash(self.password_hash, password)

    def update_last_login(self):
        """Update the user's last login timestamp"""
        self.last_login = datetime.now(timezone.utc)
        db.session.commit()

    def __repr__(self):
        return f'<User {self.username}>'

# Student model that inherits from User
# Represents a student user with additional student-specific fields
class Student(User):
    __tablename__ = 'students'
    id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    student_id = db.Column(db.String(20), unique=True)
    course = db.Column(db.String(100))
    year_of_study = db.Column(db.Integer)
    __mapper_args__ = {'polymorphic_identity': 'student'}

    def __repr__(self):
        return f'<Student {self.username}>'

# Counsellor model that inherits from User
# Represents a counsellor with specialization and availability information
class Counsellor(User):
    __tablename__ = 'counsellors'
    id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    specialization = db.Column(db.String(100))
    availability = db.Column(db.String(200))
    __mapper_args__ = {'polymorphic_identity': 'counsellor'}

    # Relationship with CounsellorAvailability model
    availabilities = db.relationship('CounsellorAvailability', back_populates='counsellor',
                                     cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Counsellor {self.username}>'

# Wellbeing Staff model that inherits from User
# Represents wellbeing staff members with department and role information
class WellbeingStaff(User):
    __tablename__ = 'wellbeing_staff'
    id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    department = db.Column(db.String(100))
    role = db.Column(db.String(100))
    __mapper_args__ = {'polymorphic_identity': 'wellbeing_staff'}

    def __repr__(self):
        return f'<WellbeingStaff {self.username}>'

# Admin model that inherits from User
# Represents system administrators
class Admin(User):
    __tablename__ = 'admins'
    id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    __mapper_args__ = {'polymorphic_identity': 'admin'}

    def __repr__(self):
        return f'<Admin {self.username}>'
    
# Wellbeing Log model for tracking student wellbeing
# Records mood, symptoms, and flags for concerning entries
class WellbeingLog(db.Model):
    __tablename__='wellbeing_logs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    mood = db.Column(db.Integer, nullable=False)  
    symptoms = db.Column(db.String(255), nullable=True)
    date_logged = db.Column(db.DateTime, default=datetime.utcnow)
    alert_flag = db.Column(db.Boolean, default=False) 

    # Relationship with Student model
    student = db.relationship('Student', backref='logs', lazy=True)

    def __repr__(self):
        return f'<WellbeingLog {self.id} - User {self.user_id}>'

# Appointment model for scheduling counselling sessions
# Links students with counsellors and tracks appointment status
class Appointment(db.Model):
    __tablename__= 'appointments'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=True)
    counsellor_id = db.Column(db.Integer, db.ForeignKey('counsellors.id'), nullable=False)
    day = db.Column(db.String(10), nullable=True)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    reason = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(50), default='Available')

    # Relationships with Student and Counsellor models
    student = db.relationship('Student', backref= 'appointments')
    counsellor = db.relationship('Counsellor', backref='appointments')
    def __repr__(self):
        return f'<Appointment {self.id}, Student {self.student_id}, Staff {self.staff_id}>'

# Counsellor Availability model for managing counsellor schedules
# Tracks when counsellors are available for appointments
class CounsellorAvailability(db.Model):
    __tablename__ = 'counsellor_availability'
    id = db.Column(db.Integer, primary_key=True)
    counsellor_id = db.Column(db.Integer, db.ForeignKey('counsellors.id'), nullable=False)
    day_of_week = db.Column(db.String(10), nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)

    # Relationship with Counsellor model
    counsellor = db.relationship('Counsellor', back_populates='availabilities')

    def __repr__(self):
        return f"<CounsellorAvailability {self.counsellor.username}, {self.day_of_week} {self.start_time}-{self.end_time}>"

# User loader for Flask-Login
# Loads the appropriate user type based on the user's type field
@login.user_loader
def load_user(id):
    try:
        # First get the base user to determine the type
        user = db.session.get(User, int(id))
        if user is None:
            return None
        
        # Then load the specific subclass based on type
        if user.type == 'student':
            return db.session.get(Student, int(id))
        elif user.type == 'counsellor':
            return db.session.get(Counsellor, int(id))
        elif user.type == 'wellbeing_staff':
            return db.session.get(WellbeingStaff, int(id))
        elif user.type == 'admin':
            return db.session.get(Admin, int(id))
        return user
    except Exception as e:
        print(f"Error loading user: {e}")
        return None

# Counselling Waitlist model for managing referral requests
# Tracks students waiting for counselling approval
class CounsellingWaitlist(db.Model):
    __tablename__='counselling_waitlist'
    student_id = db.Column(db.Integer, db.ForeignKey('students.student_id'), primary_key=True)
    student_name = db.Column(db.String(50), nullable=False)
    referral_info = db.Column(db.Text, nullable=False)
    referral_date = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship with Student model
    student = db.relationship(
        'Student',
        foreign_keys=[student_id],
        backref='referrals_about_student',
        lazy=True
    )

    def __repr__(self):
        return (f"student_id = {self.student_id}, student_name = {self.student_name}, referral_info = {self.referral_info[:20]}, referral_date = {self.referral_date}")

# Approved Referrals model for tracking approved counselling requests
# Records referrals that have been approved by wellbeing staff
class ApprovedReferrals(db.Model):
    __tablename__ = 'approved_referrals'
    student_id = db.Column(db.Integer, db.ForeignKey('students.student_id'), primary_key=True)
    student_name = db.Column(db.String(50), nullable=False)
    referral_info = db.Column(db.Text, nullable=False)
    referral_date = db.Column(db.DateTime, nullable=False)
    approved_date = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship with Student model
    student = db.relationship('Student', backref='approved_referrals', lazy=True)

    def __repr__(self):
        return f"ApprovedReferral(student_id={self.student_id}, student_name={self.student_name})"

