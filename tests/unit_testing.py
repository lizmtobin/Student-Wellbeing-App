import pytest
from app import app, db
from app.models import User, WellbeingLog

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

    with app.app_context():
        db.drop_all()
        db.create_all()
        #create test student user
        user = User(username='student1', email='student1@example.com', type='student')
        user.set_password('password123')
        db.session.add(user)
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

def test_referral_form_valid_submission(client):
    # Log in as student
    client.post('/login', data={
        'username': 'student1',
        'password': 'password123',
    }, follow_redirects=True)

    # Submit the referral form
    response = client.post('/referral_form', data={
        'referral_name': 'Bob',
        'referral_details': 'Want help with anxiety.'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Counselling Self Referral Successfully Submitted" in response.data

def test_referral_form_duplicate_submission(client):
    client.post('/login', data={
        'username': 'student1',
        'password': 'password123',
    }, follow_redirects=True)

    # First valid submission
    client.post('/referral_form', data={
        'referral_name': 'Student One',
        'referral_details': 'Initial submission.'
    }, follow_redirects=True)

    # Attempt to submit again
    response = client.post('/referral_form', data={
        'referral_name': 'Student One',
        'referral_details': 'Trying again.'
    }, follow_redirects=True)

    assert b"You have already submitted a counselling self-referral form." in response.data

def test_referral_form_non_student_access(client):
    with app.app_context():
        # Create non-student user
        user = User(username='staff1', email='staff1@example.com', type='staff')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()

    client.post('/login', data={
        'username': 'staff1',
        'password': 'password123',
    }, follow_redirects=True)

    response = client.get('/referral_form', follow_redirects=True)

    assert b"Only students have access to the the counselling self-referral form." in response.data

