# UniSupport - University Mental Health Support Platform

A Flask-based web application designed to streamline access to mental health support services for university students. The platform provides a centralized system for self-referrals, appointment booking and management, and wellbeing tracking.

## Features

### User Roles

- **Students**: Submit self-referrals, track appointments, monitor wellbeing
- **Counsellors**: Manage appointments, view assigned students, maintain session notes
- **Wellbeing Staff**: Review and process referrals, assign to counsellors, generate reports
- **Admins**: System configuration, user management, full access control

### Core Functionality

- **Self-Referral System**

  - Student-initiated counselling requests
  - Priority-based processing
  - Automated counsellor matching
  - Status tracking and notifications

- **Appointment Management**

  - Online scheduling
  - Calendar integration
  - Reminder system
  - Session notes and progress tracking

- **Wellbeing Tracker**

  - Students can log mood (1–10) and describe symptoms
  - Mood logs are visualized in a simple line chart using Chart.js
  - If mood ≤ 3, logs are flagged and shown as alerts to staff and counsellors
  - Tracker access is restricted to students only, alerts to staff only
  - Mood trend is visualized as a line chart using Chart.js
  - Chart updates dynamically based on user log history
  - Only shows when user has 2+ logs, otherwise helpful message is shown
  - Displays dates on the x-axis and mood levels on the y-axis

- **Alert System**

  - If a student's mood rating is ≤ 3, the entry is flagged with `alert_flag=True`
  - Counsellors and wellbeing staff can view flagged logs in the `/alerts` route
  - Other roles cannot access `/tracker`; staff cannot log or view student logs
  - Alerts help staff identify students who may need immediate attention

## Technical Stack

- **Backend**: Python/Flask
- **Database**: SQLite (development), PostgreSQL (production)
- **ORM**: SQLAlchemy with polymorphic inheritance
- **Authentication**: Flask-Login with role-based access control
- **Frontend**: Bootstrap 5, Font Awesome
- **Templates**: Jinja2

## Project Structure

```
unisupport/
├── app/
│   ├── __init__.py
│   ├── models.py         # Database models with polymorphic inheritance
│   ├── views.py          # Route handlers and business logic
│   ├── forms.py          # WTForms for data validation
│   ├── debug_utils.py    # Development utilities
│   ├── templates/        # Jinja2 templates
│   ├── static/
│   └── data/
├── tests/                # Test suite
├── requirements.txt      # Python dependencies
├── run.py
├── config.py
├── .gitignore
└── README.md             # Project documentation
```

## Setup and Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/yourusername/unisupport.git
   cd unisupport
   ```

2. **Initialize the database**
   You can initialize the database in two ways:

   a. Using the Flask CLI command:

   ```bash
   flask seed-db
   ```

   b. Using the Python shell:

   ```bash
   # Start Python shell
   python

   # In Python shell
   >>> from app.debug_utils import reset_db
   >>> reset_db()
   ```

   Both methods will:

   - Create all necessary database tables
   - Seed the database with test users for each role
   - Create an admin user (username: 'admin', password: 'admin123')

   Note: The database is not automatically seeded on startup. You must explicitly run one of the above commands to initialize the database.

3. **Run the development server**
   ```bash
   flask run
   ```

The application uses `.flaskenv` for environment configuration, which includes:

- FLASK_APP=app
- FLASK_ENV=development
- SECRET_KEY=your-secret-key

## Database Schema

The application uses SQLAlchemy's polymorphic inheritance to manage different user types:

- **Base User Model**: Common attributes (username, email, password)
- **Student Model**: Student-specific attributes (student_id, course)
- **Counsellor Model**: Counsellor-specific attributes (specialization, availability)
- **Wellbeing Staff Model**: Staff-specific attributes (department, role)
- **Admin Model**: Full system access

## Security Features

- Role-based access control (RBAC)
- Password hashing with Werkzeug
- Session management
- CSRF protection
- Input validation

## Development

### Debug Utilities

The application includes debug utilities for development:

- Database reset and seeding
- Test user creation
- Development-specific routes

### Testing

Run the test suite:

```bash
python -m pytest tests/
```


## Team member contribution

| Student Name & ID  | Contribution (%) | Key Contributions / Tasks Completed    | Comments (if any) | Signature |
| ------------------ | ---------------- |----------------------------------------| ----------------- |-----------|
| Vasiliki Ziaka     | 25%              | tracker, unit testing, video           |                   | VZ        |
| Alexander Bond     | 25%              | referral, unit testing, video          |                   |           |
| Nikki Evans        | 25%              | booking system, unit testing, video    |                   | NE        |
| Elizabeth Tobin    | 25%              | core structure and setup, login, video |                   |           |
| Joseph Liam Fisher | 0%               |                                        |                   |           |
