from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
import email_validator
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from model import connection
import pymysql


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
        my_cursor = connection.cursor(pymysql.cursors.DictCursor)
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
        my_cursor = connection.cursor(pymysql.cursors.DictCursor)
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
        my_cursor = connection.cursor(pymysql.cursors.DictCursor)
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