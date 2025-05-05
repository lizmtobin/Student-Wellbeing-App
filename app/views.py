from flask import (
    render_template,
    redirect,
    url_for,
    flash,
    request,
    send_file,
    send_from_directory,
)
from app import app
from app.models import User, Student, Counsellor, WellbeingStaff, WellbeingLog, CounsellingWaitlist
from app.forms import ChooseForm, LoginForm, ReferralForm, WellbeingLogForm
from flask_login import (
    current_user,
    login_user,
    logout_user,
    login_required,
    fresh_login_required,
)
import sqlalchemy as sa
from app import db
from urllib.parse import urlsplit
import csv
import io
import datetime
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
