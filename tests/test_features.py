import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from app import app, db
from app.models import User, WellbeingLog, Appointment, Counsellor, Student
from datetime import datetime, timedelta
@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

    with app.app_context():
        db.drop_all()
        db.create_all()
        
        # Create student user directly as a Student instance
        student = Student(
            username='student1',
            email='student1@example.com',
            type='student',
            student_id='12345',
            course='Test Course',
            year_of_study=1
        )
        student.set_password('password123')
        db.session.add(student)
        db.session.commit()

        # Create counsellor
        counsellor = Counsellor(username='counsellor1', email='counsellor1@example.com')
        counsellor.set_password('password123')
        db.session.add(counsellor)
        db.session.commit()

        # Create test appointment
        appointment = Appointment(
            student_id=None,
            counsellor_id=counsellor.id,
            start_time=datetime.now() + timedelta(days=1),
            end_time=datetime.now() + timedelta(days=1, hours=1),
            status='Available'
        )
        db.session.add(appointment)
        db.session.commit()

    return app.test_client()

def login(client):
    return client.post('/login', data={
        'username': 'student1',
        'password': 'password123',
        'type': 'student'
    }, follow_redirects=True)

def test_log_wellbeing_positive(client):
    """Test valid wellbeing log submission."""
    login(client)
    response = client.post('/tracker', data={
        'mood': 5,
        'symptoms': 'Feeling okay.'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Your wellbeing log has been saved.' in response.data

def test_log_wellbeing_negative(client):
    """Test invalid wellbeing log submission (mood out of range)."""
    login(client)
    response = client.post('/tracker', data={
        'mood': 100,  #invalid
        'symptoms': 'Too high mood'
    }, follow_redirects=True)

    assert b'Number must be between 1 and 10.' in response.data

def test_book_appointment_positive(client):
    """Test valid appointment booking"""
    login(client)

    with app.app_context():
        appointment = Appointment.query.filter_by(status='Available').first()
        assert appointment is not None


    response = client.post(f'/confirm_appointment/{appointment.id}', data={
        'reason': 'Need to talk'
        }, follow_redirects=True)

    assert b'Your appointment has been booked successfully' in response.data

    with app.app_context():
        updated = db.session.get(Appointment, appointment.id)
        assert updated.status == 'Booked'
        assert updated.student_id is not None


def test_book_appointment_negative(client):
    """Test invalid appointment booking (already booked)"""
    # Login as student
    login(client)
    
    with app.app_context():
        # Get the student user
        student = User.query.filter_by(username='student1').first()
        # Get an available appointment
        appointment = Appointment.query.filter_by(status='Available').first()
        # Mark it as booked by the student
        appointment.student_id = student.id
        appointment.status = 'Booked'
        db.session.commit()
        appointment_id = appointment.id

    # Try to book the already booked appointment
    response = client.post(f'/confirm_appointment/{appointment_id}', data={
        'reason': 'Trying again'
    }, follow_redirects=True)

    assert b'Sorry, this appointment has already been booked.' in response.data

#positve test case for student accessing and submitting self-referral form
def test_student_can_submit_referral(client):
    # Login as student
    client.post('/login', data={
        'username': 'student1',
        'password': 'password123',
        'type': 'student'
    }, follow_redirects=True)

    # Submit the referral form
    response = client.post('/referral_form', data={
        'referral_name': 'Student One',
        'referral_details': 'Anxiety',
        'submit': 'Submit self-referral'
    }, follow_redirects=True)

    # Check for success message and proper status
    assert response.status_code == 200
    assert b"Counselling Self Referral Successfully Submitted" in response.data

#negative test case for non-student (counsellor) attempting to access self-referral form.
def test_non_student_cannot_access_referral_form(client):
    # Login as counsellor
    client.post('/login', data={
        'username': 'counsellor1',
        'password': 'password123',
        'type': 'counsellor'
    }, follow_redirects=True)

    # Try to access referral form
    response = client.get('/referral_form', follow_redirects=True)

    # Check for access denial message
    assert response.status_code == 200
    assert b"Only students have access to the the counselling self-referral form." in response.data