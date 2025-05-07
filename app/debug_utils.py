from app import db
from app.models import User, Student, Counsellor, WellbeingStaff, Admin, WellbeingLog, CounsellorAvailability, Appointment
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta, time

def reset_db():
    """Reset the database and seed with test data"""
    print("  - Dropping all tables...")
    db.drop_all()
    print("  - Creating all tables...")
    db.create_all()
    print("  - Seeding users...")
    seed_users()
    print("  - Seeding appointments...")
    seed_appointments()
    print("  ✓ Database reset and seeded successfully!")

def seed_users():
    """Seed the database with test users"""
    print("    Creating test users...")
    
    # Create a student
    student = Student(
        username='student1',
        email='student1@example.com',
        student_id='12345',
        course='Computer Science',
        year_of_study=2
    )
    student.set_password('password123')
    db.session.add(student)
    print("    ✓ Created student1")

    # Create a counsellor
    counsellor = Counsellor(
        username='counsellor1',
        email='counsellor1@example.com',
        specialization='Anxiety and Depression'
    )
    counsellor.set_password('password123')
    db.session.add(counsellor)
    print("    ✓ Created counsellor1")

    # Create wellbeing staff
    staff = WellbeingStaff(
        username='wellbeing1',
        email='wellbeing1@example.com',
        department='Student Support',
        role='Mental Health Advisor'
    )
    staff.set_password('password123')
    db.session.add(staff)
    print("    ✓ Created wellbeing1")

    # Create admin
    admin = Admin(
        username='admin',
        email='admin@example.com'
    )
    admin.set_password('admin123')
    db.session.add(admin)
    print("    ✓ Created admin")

    # Commit all users
    db.session.commit()
    print("    ✓ All users committed to database")

    # Add availabilities for counsellor
    print("    Creating counsellor availabilities...")
    for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']:
        availability = CounsellorAvailability(
            counsellor_id=counsellor.id,
            day_of_week=day,
            start_time=time(9, 0),
            end_time=time(17, 0)
        )
        db.session.add(availability)
    
    db.session.commit()
    print("    ✓ Counsellor availabilities created")

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
