from random import choices
from re import sub
from secrets import choice
from tkinter.tix import Select
from jmespath import search
from datetime import datetime, date
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField,IntegerField
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

    date_of_birth = DateTimeField('date_of_birth', format='%Y-%m-%d', validators=[DataRequired()])
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


class customerpurchaseForm(FlaskForm):
    submit = SubmitField(label = 'Buy_ticket')


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
    
    
    

class statuscheckForm(FlaskForm):
    fnumber = StringField("Flight Number", validators=[DataRequired()])
    submit = SubmitField()
    
    
class airplaneForm(FlaskForm):
    planeid = StringField("Plane ID", validators=[DataRequired()])
    seats = IntegerField("Seat Number", validators=[DataRequired()])
    submit = SubmitField("Submit")
    def validate_planeid(self,planeid):
        if not planeid.data.isdigit():
            raise ValidationError('Please enter valid digits.')




class Airline_staff_LoginForm(FlaskForm):
    username = StringField('Username',
                       validators=[DataRequired(), Length(max=50)])

    password = PasswordField('Password',
                        validators=[DataRequired()])
    airline_name = StringField('Airline Name',
                        validators=[DataRequired()])

    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')
    
class rangeForm(FlaskForm):
    dateone = DateField('Dateone',
                        validators=[DataRequired()])
    datetwo = DateField('Datetwo',
                        validators=[DataRequired()])
    submit = SubmitField('Submit')
    


class Booking_agent_LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])

    password = PasswordField('Password',
                        validators=[DataRequired()])
    Id = StringField('Booking Agent ID',
                        validators=[DataRequired()])

    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class Staff_insert_airplane_Form(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    submit = SubmitField('Login')

class Staff_insert_airport_Form(FlaskForm):
    airport_name = StringField('Airport Name',
                        validators=[DataRequired()])
    airport_city = StringField('Airport_City',
                              validators=[DataRequired()])
    submit = SubmitField('Submit')

    def validate_airport(self, airport_name):
        with model.staff_connection.cursor(pymysql.cursors.DictCursor) as mycursor:
            str_airport_name = str(airport_name.data)
            query = f"Select airport_name from airline_available_airports where airport_name = '{str_airport_name}' "
            mycursor.execute(query)
            data = mycursor.fetchall()
            mycursor.close()
            print(data)
            if data:
                raise ValidationError('Airport Already in System')


class Staff_grant_permission_Form(FlaskForm):
    username = StringField('Admin Username',
                        validators=[DataRequired()])
    status = StringField('Permission Type',
                              validators=[DataRequired()])
    submit = SubmitField('Submit')

    def validate_status(self, status):
        status_type = ['Admin', 'Operator']
        if str(status.data) not in status_type:
            raise ValidationError('Please type the right status')





class Staff_add_booking_agent_Form(FlaskForm):

    email = StringField('Booking_agent email',
                        validators=[DataRequired(), Email()])

    submit = SubmitField('Submit')

    def validate_email(self, email):
        with model.staff_connection.cursor(pymysql.cursors.DictCursor) as mycursor:
            str_email = str(email.data)
            query = f"Select email from booking_agent where email = '{str_email}'"
            mycursor.execute(query)
            data = mycursor.fetchone()
            mycursor.close()
            if data is None:
                raise ValidationError('Agent is not registered')

class Operator_Update_Flight_Form(FlaskForm):
    flight_num = StringField('Flight Number',
                        validators=[DataRequired()])
    flight_status = StringField('Update Flight Status to',
                        validators=[DataRequired()])
    submit = SubmitField('Submit')

    def validate_flight_status(self, flight_status):
        status_type = ['Upcoming', 'Delayed', 'In Progress']
        if str(flight_status.data) not in status_type:
            raise ValidationError('Please type the right status')

class add_flight_form(FlaskForm):
    dep_airport_name = StringField('Departure Airport Name',
                               validators=[DataRequired()])
    arr_airport_name = StringField('Arrival Airport Name',
                               validators=[DataRequired()])

    dep_time = DateTimeField('Dep_time', format="%Y-%m-%d %H:%M:%S",
                        validators=[DataRequired()])

    arr_time = DateTimeField("Arrival Time", format="%Y-%m-%d %H:%M:%S",
                           validators=[DataRequired()])

    price = StringField("Price",
                        validators=[DataRequired()])
    status = StringField("Status",
                        validators=[DataRequired()])
    airplane_id = IntegerField("Airplane ID",
                           validators=[DataRequired()])

    submit = SubmitField('Submit')



