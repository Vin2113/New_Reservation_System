from random import choices
from secrets import choice
from tkinter.tix import Select
from jmespath import search
from datetime import datetime, date
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField
from wtforms.fields import DateTimeField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from wtforms_components import DateRange
from Reservation import login_manager
from model import my_cursor

@login_manager.user_loader
def load_user(email):
    query = f"SELECT email from customer WHERE email = '{email}'"
    my_cursor.execute(query)
    user = [i[0] for i in my_cursor if i[0] == email ]
    return user

class RegistrationForm(FlaskForm):
    name = StringField('Name',
                           validators=[DataRequired(), Length(max=50)])
    email = StringField('Email',
                           validators=[DataRequired(), Email()])

    password = PasswordField('Password',
                           validators=[DataRequired(), Length(max=20)])
    confirm_password = PasswordField('Confirm Password',
                           validators=[DataRequired(), EqualTo('password')])

    building_number = StringField('building number',
                        validators=[DataRequired(), Length(max=30)])
    street = StringField('street',
                        validators=[DataRequired(), Length(max=30)])
    city = StringField('city',
                        validators=[DataRequired(), Length(max=30)])
    state = StringField('state',
                        validators=[DataRequired(), Length(max=30)])
    phone_number = StringField('phone_number',
                        validators=[DataRequired(), Length(max=11)])
    passport_number = StringField('passport_number',
                               validators=[DataRequired(), Length(max=30)])
    passport_expiration = StringField('passport_expiration',
                               validators=[DataRequired(), Length(max=50)])
    passport_country = StringField('passport_country',
                               validators=[DataRequired(), Length(max=50)])
    date_of_birth = StringField('date_of_birth',
                               validators=[DataRequired(), Length(max=10)])

    submit = SubmitField('Sign Up')

    def validate_email(self, email):
        str_email = str(email.data)
        query = f"SELECT email from customer WHERE email = '{str_email}'"
        my_cursor.execute(query)
        user = [i[0] for i in my_cursor if i[0] == str_email]
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')


class LoginForm(FlaskForm):
    email = StringField('Email',
                           validators=[DataRequired(), Email()])

    password = PasswordField('Password',
                           validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class SearchForm(FlaskForm):
    depart = SelectField("Departure", choices =[],validate_choice=False)
    arrival = SelectField("Arrival", choices =[],validate_choice=False)
    time = DateTimeField()

