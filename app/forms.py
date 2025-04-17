from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import SubmitField, HiddenField, StringField, BooleanField, SelectField, IntegerField, TextAreaField, PasswordField
from wtforms.fields.numeric import IntegerField
from wtforms.fields.simple import TextAreaField
from wtforms.validators import DataRequired, NumberRange, ValidationError, Email, Optional, Length
from app import db
from app.models import User
import datetime

from wtforms.validators import ValidationError
import re


class ChooseForm(FlaskForm):
    choice = HiddenField('Choice')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    type = SelectField('User Type', choices=[
        ('student', 'Student'),
        ('counsellor', 'Counsellor'),
        ('wellbeing_staff', 'WellBeing Staff'),
        ('admin', 'Admin')
    ], validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

def validate_words_only(form, field):
    #strip input and check for at least one valid word (letters only)
    if not field.data or not re.search(r'\b[a-zA-Z]{2,}\b', field.data):
        raise ValidationError("Please describe your symptoms using at least one valid word.")

class WellbeingLogForm(FlaskForm):
    mood = IntegerField(
        'Mood rating (1-10)',
        validators=[DataRequired(), 
                    NumberRange(min=1, max=10)])
    symptoms = TextAreaField(
        'Symptoms',
        validators=[DataRequired(), 
                    validate_words_only,
                    Length(max=300, message='Please keep symptoms under 300 characters.')]) 
    submit = SubmitField('Log entry')
