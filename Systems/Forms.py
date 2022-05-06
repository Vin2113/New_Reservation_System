from random import choices
from secrets import choice
from tkinter.tix import Select
from jmespath import search
from datetime import datetime, date
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField
from wtforms.fields import DateTimeField, DateField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError,Optional
from wtforms_components import DateRange
from Reservation import login_manager
import model
import pymysql
@login_manager.user_loader
def load_user(email):
    with model.connection.cursor() as my_cursor:
        query = f"SELECT email from customer WHERE email = '{email}'"
        my_cursor.execute(query)
        user = [i[0] for i in my_cursor if i[0] == email ]
        return user

class SearchForm(FlaskForm):
    depart = SelectField("Departure", choices =[],validate_choice=False)
    arrival = SelectField("Arrival", choices =[],validate_choice=False)
    time = DateTimeField()

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
    passport_expiration = DateTimeField('passport_expiration', format ='%Y-%m-%d', validators=[DataRequired()])
    passport_country = StringField('passport_country',
                                validators=[DataRequired(), Length(max=50)])
    date_of_birth = DateTimeField('date_of_birth',format ='%Y-%m-%d', validators=[DataRequired()])

    submit = SubmitField('Sign Up')

    def validate_email(self, email):
        str_email = str(email.data)
        query = f"SELECT email from customer WHERE email = '{str_email}'"
        my_cursor = model.connection.cursor(pymysql.cursors.DictCursor)
        my_cursor.execute(query)
        user = my_cursor.fetchone()
        my_cursor.close()
        if user:
            raise ValidationError('This email is taken. Please choose a different one.')

class Agent_RegistrationForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password',
                           validators=[DataRequired(), Length(max=20)])

    confirm_password = PasswordField('Confirm Password',
                           validators=[DataRequired(), EqualTo('password')])
    Id = StringField('Booking Agent ID',
                        validators=[DataRequired()])
    submit = SubmitField('Register')
    def validate_email(self, email):
        str_email = str(email.data)
        query = f"SELECT email from booking_agent WHERE email = '{str_email}'"
        my_cursor = model.connection.cursor(pymysql.cursors.DictCursor)
        my_cursor.execute(query)
        user = my_cursor.fetchone()
        my_cursor.close()
        if user:
            raise ValidationError('This email is taken. Please choose a different one.')

class Airline_staff_RegistrationForm(FlaskForm):
    username = StringField('Username',
                       validators=[DataRequired(), Length(max=50)])
    first_name = StringField('First Name',
                       validators=[DataRequired(), Length(max=50)])
    last_name = StringField('Last Name',
                       validators=[DataRequired(), Length(max=50)])

    password = PasswordField('Password',
                        validators=[DataRequired()])

    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    airline_name = StringField('Airline Name',
                        validators=[DataRequired()])

    date_of_birth = StringField('Date of Birth mm/dd/yyyy',
                               validators=[DataRequired(), Length(max=10)])
    submit = SubmitField('Register')
    def validate_username(self, username):
        str_username = str(username.data)
        query = f"SELECT username from airline_staff WHERE username = '{str_username}'"
        my_cursor = model.connection.cursor(pymysql.cursors.DictCursor)
        my_cursor.execute(query)
        user = my_cursor.fetchone()
        my_cursor.close()
        if user:
            raise ValidationError('This email is taken. Please choose a different one.')



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
    time = StringField("Departure Date")

class Airline_staff_LoginForm(FlaskForm):
    name = StringField('Username',
                       validators=[DataRequired(), Length(max=50)])

    password = PasswordField('Password',
                        validators=[DataRequired()])
    airline_name = StringField('Airline Name',
                        validators=[DataRequired()])

    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class Booking_agent_LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])

    password = PasswordField('Password',
                        validators=[DataRequired()])
    Id = StringField('Booking Agent ID',
                        validators=[DataRequired()])

    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')