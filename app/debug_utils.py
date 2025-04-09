from app import db
from app.models import User, Student, Counsellor, WellbeingStaff, Admin
from werkzeug.security import generate_password_hash


def reset_db():
    """Reset the database and seed with test data"""
    db.drop_all()
    db.create_all()
    seed_users()


def seed_users():
    """Seed the database with test users"""
    # Test users data
    test_users = [
        {
            'username': 'student1',
            'email': 'student1@example.com',
            'password': 'password123',
            'type': 'student',
            'student_id': '12345',
            'course': 'Computer Science',
            'year_of_study': 2
        },
        {
            'username': 'counsellor1',
            'email': 'counsellor1@example.com',
            'password': 'password123',
            'type': 'counsellor',
            'specialization': 'Anxiety and Depression',
            'availability': 'Monday-Friday 9am-5pm'
        },
        {
            'username': 'wellbeing1',
            'email': 'wellbeing1@example.com',
            'password': 'password123',
            'type': 'wellbeing_staff',
            'department': 'Student Support',
            'role': 'Mental Health Advisor'
        },
        {
            'username': 'admin',
            'email': 'admin@example.com',
            'password': 'admin123',
            'type': 'admin'
        }
    ]

    # Create and add users
    for user_data in test_users:
        if user_data['type'] == 'student':
            user = Student(
                username=user_data['username'],
                email=user_data['email'],
                student_id=user_data['student_id'],
                course=user_data['course'],
                year_of_study=user_data['year_of_study']
            )
        elif user_data['type'] == 'counsellor':
            user = Counsellor(
                username=user_data['username'],
                email=user_data['email'],
                specialization=user_data['specialization'],
                availability=user_data['availability']
            )
        elif user_data['type'] == 'wellbeing_staff':
            user = WellbeingStaff(
                username=user_data['username'],
                email=user_data['email'],
                department=user_data['department'],
                role=user_data['role']
            )
        elif user_data['type'] == 'admin':
            user = Admin(
                username=user_data['username'],
                email=user_data['email']
            )
        
        user.set_password(user_data['password'])
        db.session.add(user)

    db.session.commit()
