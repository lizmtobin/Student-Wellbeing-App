from flask import render_template, redirect, url_for, flash, request, send_file, send_from_directory
from app import app
from app.models import User, Student, Counsellor, WellbeingStaff
from app.forms import ChooseForm, LoginForm
from flask_login import current_user, login_user, logout_user, login_required, fresh_login_required
import sqlalchemy as sa
from app import db
from urllib.parse import urlsplit
import csv
import io
import datetime
from app.debug_utils import reset_db


@app.route("/")
def home():
    return render_template('home.html', title="Home")


@app.route("/account")
@login_required
def account():
    return render_template('account.html', title="Account", user=current_user)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    form = LoginForm()
    if form.validate_on_submit():
        # Here you would typically integrate the university's authentication system
        # Instead, we just check if the user exists and has the correct type
        user = db.session.scalar(
            sa.select(User).where(User.username == form.username.data))
        
        if user is None:
            flash('User not found. Please contact the system administrator.', 'danger')
            return redirect(url_for('login'))
        
        if user.type != form.type.data:
            flash('Invalid user type selection.', 'danger')
            return redirect(url_for('login'))
        
        # In a real implementation, you would verify the user's credentials
        # with the university's authentication system here
        # This is where we would make the API call to the university's auth system
        # with form.username.data and form.password.data
        
        # For now, we'll just check if the password matches
        if not user.check_password(form.password.data):
            flash('Invalid password.', 'danger')
            return redirect(url_for('login'))
        
        login_user(user, remember=form.remember_me.data)
        user.update_last_login()
        
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('home')
        return redirect(next_page)
    
    return render_template('generic_form.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


# Debug route to reset database - go to the url /debug/reset-db to reset the database
@app.route('/debug/reset-db')
def debug_reset_db():
    reset_db()
    flash('Database has been reset with test data.', 'success')
    return redirect(url_for('home'))


# Error handlers
# See: https://en.wikipedia.org/wiki/List_of_HTTP_status_codes

# Error handler for 403 Forbidden
@app.errorhandler(403)
def error_403(error):
    return render_template('errors/403.html', title='Error'), 403

# Handler for 404 Not Found
@app.errorhandler(404)
def error_404(error):
    return render_template('errors/404.html', title='Error'), 404

@app.errorhandler(413)
def error_413(error):
    return render_template('errors/413.html', title='Error'), 413

# 500 Internal Server Error
@app.errorhandler(500)
def error_500(error):
    return render_template('errors/500.html', title='Error'), 500