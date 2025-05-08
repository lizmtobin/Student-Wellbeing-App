# UniSupport - University Mental Health Support Platform

A Flask-based web application designed to streamline access to mental health support services for university students. The platform provides a centralized system for self-referrals, appointment booking and management, and wellbeing tracking.

## Features

### User Roles

- **Students**: Submit self-referrals, track appointments, monitor wellbeing
- **Counsellors**: Manage appointments, view assigned students, maintain session notes
- **Wellbeing Staff**: Review and process referrals, assign to counsellors, generate reports
- **Admins**: System configuration, user management, full access control

### Core Features

- **Self-Referral System**

  - Student-initiated counselling requests
  - Priority-based processing
  - Automated counsellor matching
  - Status tracking and notifications

- **Appointment Management**

  - Book Appointment: Students view and book available slots grouped by date.
    Each slot shows time and counsellor.

  - Confirm Appointment: After selecting a slot, students enter a reason to confirm the booking.
    The system updates the slot status to “Booked.”

  - Create Slot: Counsellors can add new appointment slots by specifying start/end time
    and an optional note. These appear as bookable for students.

- **Wellbeing Tracker**

  - Students can log mood (1–10) and describe symptoms
  - Mood logs are visualized in a simple line chart using Chart.js
  - If mood ≤ 3, logs are flagged and shown as alerts to staff and counsellors
  - Tracker access is restricted to students only, alerts to staff only
  - Mood trend is visualized as a line chart using Chart.js
  - Chart updates dynamically based on user log history
  - Only shows when user has 2+ logs, otherwise helpful message is shown
  - Displays dates on the x-axis and mood levels on the y-axis

- **Alert System for Wellbeing Tracker**

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
│   └── data/             # SQLite  database
├── tests/                # Test suite
├── requirements.txt      # Python dependencies
├── run.py                # Runs the whole app
├── config.py
├── .gitignore            # Files to ignore on commit
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
   # From the console start the shell 
   flask shell

   # In shell write:
   >>> reset_db()
   ```

   Both methods will:

   - Create all necessary database tables
   - Seed the database with test users for each role
   - Create an admin user (username: 'admin', password: 'admin123')
   - As only Authorised Users can login, you will need to seed Users to test the App

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

The test_features.py file holds the tests for the 3 core features of the app (referral, booking system, wellbeing tracker).  
There is one positive and one negative test for each.

Run the test suite:

```bash
python -m pytest tests/
```

 if pytest is already installed and accessible globally, you just run:
```
 pytest tests/
```

###DEVELOPEMENT NOTES

### Database Relationships
The application uses a polymorphic inheritance pattern for user management with the following key relationships:

- **User Hierarchy**:
  - Base `User` model with polymorphic inheritance
  - Specialized models: `Student`, `Counsellor`, `WellbeingStaff`, and `Admin`
  - Each user type has specific attributes and relationships

- **Role-Based Access Control**
   - Secure authentication system
   - Role-specific dashboards and functionalities
   - Protected routes and resources

### Design Patterns
- **Polymorphic Inheritance**: Used for user management to maintain clean separation of concerns
- **Repository Pattern**: Database operations are encapsulated within model classes
- **Factory Pattern**: User creation and management
- **MVC Architecture**: Clear separation of models, views, and controller(View for routing/decorators)

### Development Methodology
The project was developed using an iterative Agile approach:

- **User Stories**: Feature development driven by user requirements as scoped out in Assignment1.
- **Continuous Integration**: Regular code integration and collaboration via Teams & Github.
- **Incremental Development**: Features added iteratively with regular feedback including acting as QA for eachothers work.

### Future Iterations

#### AI-Enhanced Features (Next Phase)
The next iteration of UniSupport will incorporate AI capabilities to enhance the support system.

## Team member contribution

| Student Name & ID  | Contribution (%) | Key Contributions / Tasks Completed    | Comments (if any) | Signature |
| ------------------ | ---------------- |----------------------------------------| ----------------- |-----------|
| Vasiliki Ziaka     | 25%              | tracker, unit testing, video           |                   | VZ        |
| Alexander Bond     | 25%              | referral, unit testing, video          |                   | AB        |
| Nikki Evans        | 25%              | booking system, unit testing, video    |                   | NE        |
| Elizabeth Tobin    | 25%              | core structure and setup, login, video |                   | ET        |
| Joseph Liam Fisher | 0%               |                                        |                   |           |

