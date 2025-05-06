from flask import (
    render_template,
    redirect,
    url_for,
    flash,
    request,
    send_file,
    send_from_directory,
)

from app import app, db
from app.models import User, Student, Counsellor, WellbeingStaff, WellbeingLog, Appointment, CounsellorAvailability, CounsellingWaitlist
from app.forms import ChooseForm, LoginForm, ReferralForm, WellbeingLogForm, AppointmentForm, AddSlotForm
from flask_login import (
    current_user,
    login_user,
    logout_user,
    login_required,
    fresh_login_required,
)
import sqlalchemy as sa
from urllib.parse import urlsplit
import csv
import io
from datetime import datetime, time
from app.debug_utils import reset_db


@app.route("/")
def home():
    return render_template("home.html", title="Home")


@app.route("/account")
@login_required
def account():
    return render_template("account.html", title="Account", user=current_user)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    form = LoginForm()
    if form.validate_on_submit():
        # Here you would typically integrate the university's authentication system
        # Instead, we just check if the user exists and has the correct type
        user = db.session.scalar(
            sa.select(User).where(User.username == form.username.data)
        )

        if user is None:
            flash("User not found. Please contact the system administrator.", "danger")
            return redirect(url_for("login"))

        if user.type != form.type.data:
            flash("Invalid user type selection.", "danger")
            return redirect(url_for("login"))

        # In a real implementation, you would verify the user's credentials
        # with the university's authentication system here
        # This is where we would make the API call to the university's auth system
        # with form.username.data and form.password.data

        # For now, we'll just check if the password matches
        if not user.check_password(form.password.data):
            flash("Invalid password.", "danger")
            return redirect(url_for("login"))

        login_user(user, remember=form.remember_me.data)
        user.update_last_login()

        next_page = request.args.get("next")
        if not next_page or urlsplit(next_page).netloc != "":
            next_page = url_for("home")
        return redirect(next_page)

    return render_template("generic_form.html", title="Sign In", form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))


@app.route("/referral_form", methods=["GET", "POST"])
@login_required
def referral_form():
    if not isinstance(current_user, Student):
        flash(
            "Only students have access to the the counselling self-referral form.",
            "danger",
        )
        return redirect(url_for("home"))

    form = ReferralForm()
    if form.validate_on_submit():
        student_id = form.referral_id.data
        student_name = form.referral_name.data
        referral_info = form.referral_details.data
        new_referral = CounsellingWaitlist(student_id=student_id, student_name=student_name, referral_info=referral_info)
        db.session.add(new_referral)
        db.session.commit()
        #Above code adds new referral to the database using data submitted via the self-referral form.
        flash(f"Counselling Self Referral Successfully Submitted")
        return redirect(url_for("home"))
    return render_template(
        "referral_form.html", title="Counselling Self-Referral Form", form=form
    )

@app.route("/view_waitlist")
#@login_required
def view_waitlist():
#    if not isinstance(current_user, WellbeingStaff):
#        flash(
#            "Only wellbeing-staff can view the counselling waiting list.",
#            "danger",
#        )
#        return redirect(url_for("home"))
    referrals = CounsellingWaitlist.query.all()
    return render_template('waitlist.html', referrals=referrals)


# Debug route to reset database - go to the url /debug/reset-db to reset the database
@app.route("/debug/reset-db")
def debug_reset_db():
    reset_db()
    flash("Database has been reset with test data.", "success")
    return redirect(url_for("home"))


@app.route("/tracker", methods=["GET", "POST"])
@login_required
def wellbeing_tracker():
    # allow only students to access the tracker as they are the only ones
    # who can log moods
    if not isinstance(current_user, Student):
        flash(
            "Only students have access to the wellbeing tracker logs and form.",
            "danger",
        )
        return redirect(url_for("home"))

    form = WellbeingLogForm()

    if form.validate_on_submit():
        mood = form.mood.data
        symptoms = form.symptoms.data

        # flag if mood is critically low (3 or below)
        alert = mood <= 3

        new_log = WellbeingLog(
            user_id=current_user.id, mood=mood, symptoms=symptoms, alert_flag=alert
        )

        db.session.add(new_log)
        db.session.commit()

        flash("Your wellbeing log has been saved.", "success")

        return redirect(url_for("wellbeing_tracker"))

    logs = (
        WellbeingLog.query.filter_by(user_id=current_user.id)
        .order_by(WellbeingLog.date_logged.asc())
        .all()
    )
    return render_template(
        "wellbeing_tracker.html", title="Wellbeing Tracker", form=form, logs=logs
    )


@app.route("/alerts")
@login_required
def view_alerts():
    if not isinstance(current_user, (Counsellor, WellbeingStaff)):
        flash(
            "Access denied. Alerts are only available to wellbeing staff and counsellors.",
            "danger",
        )
        return redirect(url_for("home"))

    alerts = (
        WellbeingLog.query.filter_by(alert_flag=True)
        .order_by(WellbeingLog.date_logged.desc())
        .all()
    )
    return render_template("alerts.html", title="Alerts", alerts=alerts)


@app.route("/book/appointment", methods=["GET", "POST"])
@login_required
def book_appointment():
    form=AppointmentForm()
    available_appointments = Appointment.query.filter_by(status='Available').order_by(Appointment.start_time).all()

    return render_template('book_appointment.html', title="Book Appointment",  available_appointments=available_appointments, form=form)




@app.route('/confirm_appointment/<int:appointment_id>', methods=['GET', 'POST'])
@login_required
def confirm_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    form=AppointmentForm()
    if appointment.student_id is not None:
        flash('Sorry, this appointment has already been booked.', 'danger')
        return redirect(url_for('book_appointment'))

    if request.method == 'POST':
        reason = request.form.get('reason')

        if not reason:
            flash('Please provide a reason for your appointment.', 'warning')
            return redirect(request.url)

        appointment.student_id = current_user.id
        appointment.reason = reason
        appointment.status = 'Booked'
        db.session.commit()

        flash('Your appointment has been booked successfully!', 'success')
        return redirect(url_for('view_appointment'))

    return render_template('confirm_appointment.html', title="Confirm Appointment", appointment=appointment, form=form)

@app.route('/view_appointment')
@login_required
def view_appointment():
    if not isinstance(current_user, Student):
        flash("Only students can view their booked appointments.", "danger")
        return redirect(url_for("home"))

    appointments = Appointment.query.filter_by(student_id=current_user.id).order_by(Appointment.start_time.asc()).all()

    return render_template('view_appointment.html', title="View Appointment", appointments=appointments)


@app.route("/counsellor/appointments")
@login_required
def counsellor_appointments():
    if not isinstance(current_user, Counsellor):
        flash("Only counsellors can view this page.", "danger")
        return redirect(url_for("home"))

    appointments = Appointment.query.filter_by(counsellor_id=current_user.id).order_by(Appointment.start_time.asc()).all()

    return render_template('counsellor_appointments.html', title='View Appointments', appointments=appointments)


@app.route("/counsellor/add_slot", methods=["GET", "POST"])
@login_required
def add_slot():
    if not isinstance(current_user, Counsellor):
        flash("Only counsellors can add slots.", "danger")
        return redirect(url_for('home'))

    form = AddSlotForm()

    if form.validate_on_submit():
        new_slot = Appointment(
            counsellor_id=current_user.id,
            start_time=form.start_time.data,
            end_time=form.end_time.data,
            status='available'
        )
        db.session.add(new_slot)
        db.session.commit()

        flash("New slot added successfully!", "success")
        return redirect(url_for('counsellor_calendar'))

    return render_template('add_slot.html', title='Add New Slot', form=form)

# Error handlers
# See: https://en.wikipedia.org/wiki/List_of_HTTP_status_codes


# Error handler for 403 Forbidden
@app.errorhandler(403)
def error_403(error):
    return render_template("errors/403.html", title="Error"), 403


# Handler for 404 Not Found
@app.errorhandler(404)
def error_404(error):
    return render_template("errors/404.html", title="Error"), 404


@app.errorhandler(413)
def error_413(error):
    return render_template("errors/413.html", title="Error"), 413


# 500 Internal Server Error
@app.errorhandler(500)
def error_500(error):
    return render_template("errors/500.html", title="Error"), 500
