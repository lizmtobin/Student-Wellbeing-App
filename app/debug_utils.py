from app import db
from app.models import User, Student, Counsellor, WellbeingStaff, Admin, WellbeingLog, CounsellorAvailability, Appointment
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta, time



def reset_db():
    """Reset the database and seed with test data"""
    # print("RESETTING DATABASE...")
    db.drop_all()
    db.create_all()
    seed_users()
    seed_appointments()


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
            'availability': [
                ('Monday', time(9, 0), time(17, 0)),
                ('Tuesday', time(9, 0), time(17, 0)),
                ('Wednesday', time(9, 0), time(17, 0)),
                ('Thursday', time(9, 0), time(17, 0)),
                ('Friday', time(9, 0), time(17, 0))
            ]
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
            )
            db.session.add(user)
            db.session.commit()

            availability_data = user_data.get('availability', [])
            for day, start_time, end_time in availability_data:
                availability = CounsellorAvailability(
                    counsellor_id=user.id,
                    day_of_week=day,
                    start_time=start_time,
                    end_time=end_time
                )
                db.session.add(availability)

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




def seed_appointments():
    day_name_to_num = {
        'Monday': 0, 'Tuesday': 1, 'Wednesday': 2,
        'Thursday': 3, 'Friday': 4, 'Saturday': 5, 'Sunday': 6
    }

    today = datetime.today()

    availabilities = CounsellorAvailability.query.all()

    for availability in availabilities:
        counsellor = availability.counsellor
        day_of_week = availability.day_of_week
        start_time = availability.start_time
        end_time = availability.end_time


        target_weekday = day_name_to_num[day_of_week]
        days_ahead = (target_weekday - today.weekday() + 7) % 7
        if days_ahead == 0:
            days_ahead = 7

        appointment_date = today + timedelta(days=days_ahead)

        start_datetime = datetime.combine(appointment_date.date(), start_time)
        end_datetime = datetime.combine(appointment_date.date(), end_time)

        current_start = start_datetime
        while current_start + timedelta(minutes=30) <= end_datetime:
            existing_appointment = Appointment.query.filter(
                Appointment.counsellor_id == counsellor.id,
                Appointment.start_time == current_start
            ).first()

            if not existing_appointment:
                appointment = Appointment(
                    student_id=None,
                    counsellor_id=counsellor.id,
                    day=day_of_week,
                    start_time=current_start,
                    end_time=current_start + timedelta(minutes=30),
                    reason=None,
                    status='Available'
                )
                db.session.add(appointment)

            current_start += timedelta(minutes=30)

    db.session.commit()