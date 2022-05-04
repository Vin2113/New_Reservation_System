from Reservation import app, bcrypt
from Forms import RegistrationForm, Agent_RegistrationForm, Airline_staff_RegistrationForm, LoginForm, Booking_agent_LoginForm, Airline_staff_LoginForm
from flask_login import login_user, current_user, logout_user, login_required
from flask import render_template, flash, redirect, session, request, url_for
import datetime
import model
import pymysql.cursors
import cryptography
@app.route('/')
@app.route('/home')
def home():
    '''    with connection.cursor(pymysql.cursors.DictCursor) as mycursor:
        query = "select * from flight where status = 'Upcoming'"
        mycursor.execute(query)
        data = mycursor.fetchall()
        mycursor.close()'''

    return render_template('Layout.html', title='Home')

@app.route('/register', methods=["GET", 'POST'])

def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        # #verify email unique
        #insert into database
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        phone_number = int(str(form.phone_number.data))
        email = str(form.email.data)
        exp_time = datetime.datetime(int(form.passport_expiration.data[-4:-1]), int(form.passport_expiration.data[0:2]), int(form.passport_expiration.data[3:5]))
        dob_time = datetime.datetime(int(form.date_of_birth.data[-4:-1]), int(form.date_of_birth.data[0:2]), int(form.date_of_birth.data[3:5]))
        query = f"Insert INTO customer VALUES('{email}', '{form.name.data}', '{hashed_password}','{form.building_number.data}','{form.street.data}','{form.city.data}','{form.state.data}', {phone_number} ,'{form.passport_number.data}','{exp_time}','{form.passport_country.data}','{dob_time}')"
        my_cursor = model.connection.cursor()
        my_cursor.execute(query)
        model.connection.commit()
        my_cursor.close()
        flash(f'You can now login {form.name.data}!', 'success')
        return redirect(url_for('login'))
    return render_template('Register.html', title='Register', form=form)
@app.route('/agent_register', methods=["GET", 'POST'])
def agent_register():
    form = Agent_RegistrationForm()
    if form.validate_on_submit():
        # #verify email unique
        #insert into database
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        email = str(form.email.data)
        query = f"Insert INTO booking_agent VALUES('{email}', '{hashed_password}','{form.Id.data}',)"
        my_cursor = model.connection.cursor()
        my_cursor.execute(query)
        model.connection.commit()
        my_cursor.close()
        flash(f'You can now login {form.email.data}!', 'success')
        return redirect(url_for('agent_login'))
    return render_template('agent_register.html', title='Register', form=form)

@app.route('/staff_register', methods=["GET", 'POST'])
def staff_register():
    form = Airline_staff_RegistrationForm()
    if form.validate_on_submit():
        # #verify email unique
        #insert into database
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        username = str(form.username.data)
        dob_time = datetime.datetime(int(form.date_of_birth.data[-4:-1]), int(form.date_of_birth.data[0:2]),
                                     int(form.date_of_birth.data[3:5]))
        query = f"Insert INTO airline_staff VALUES('{username}', '{hashed_password}','{form.first_name.data}','{form.last_name.data}', {dob_time}, '{form.airline_name.data}',)"
        my_cursor = model.connection.cursor()
        my_cursor.execute(query)
        model.connection.commit()
        my_cursor.close()
        flash(f'You can now login {form.first_name.data}!', 'success')
        return redirect(url_for('staff_login'))
    return render_template('staff_register.html', title='Register', form=form)


@app.route('/customer_login', methods=["GET", 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        str_email = str(form.email.data)
        query = f"SELECT email, password from customer WHERE email = '{str_email}'"
        my_cursor = model.connection.cursor()
        my_cursor.execute(query)
        account = my_cursor.fetchone()
        #checking user data from database for verification
        if account and bcrypt.check_password_hash(account[1],form.password.data):
            session['type'] = 'customer'
            session['loggedin'] = True
            session['customer'] = account[0]
            session['password'] = account[1]
            flash('Login Successful', 'success')
            return redirect(url_for('home'))
        else:
            flash('Login unsuccesful, please check Email and Password.', 'danger')
    return render_template('Login.html', title='Login', form=form)

@app.route('/agent_login', methods=["GET", 'POST'])
def agent_login():
    form = Booking_agent_LoginForm()
    if form.validate_on_submit():
        str_email = str(form.email.data)
        id = str(form.Id.data)
        query = f"SELECT email, password, booking_agent_id from booking_agent WHERE email = '{str_email}'"
        my_cursor = model.connection.cursor()
        my_cursor.execute(query)
        account = my_cursor.fetchone()
        # checking user data from database for verification
        if account[0] != str_email and bcrypt.check_password_hash(account[1], form.password.data) and id == account[2]:
            session['type'] = 'agent'
            session['loggedin'] = True
            session['customer'] = account[0]
            session['password'] = account[1]
            flash('Login Successful', 'success')
            return redirect(url_for('home'))
        else:
            flash('Login unsuccesful, please check Email, Password, and ID.', 'danger')
    return render_template('Agent_login.html', title='Login', form=form)

@app.route('/staff_login', methods=["GET", 'POST'])
def staff_login():
    form = Airline_staff_LoginForm()
    if form.validate_on_submit():
        str_username = str(form.name.data)
        query = f"SELECT username, password, airline_name From airline_staff  WHERE username = '{str_username}'"
        my_cursor = model.connection.cursor()
        my_cursor.execute(query)
        account = my_cursor.fetchone()
        my_cursor.close()
        # checking user data from database for verification
        if account != None and account[0] != str_username and bcrypt.check_password_hash(account[1], form.password.data):
            session['type'] = 'staff'
            session['loggedin'] = True
            session['username'] = account[0]
            session['password'] = account[1]
            session['airline'] = account[2]
            flash('Login Successful', 'success')
            with model.staff_connection.cursor() as mycursor:
                query = f"SELECT permission_type From permission WHERE username = {str_username}"
                mycursor.execute(query)
                data = mycursor.fetchall()
                for i in data:
                    if i == "Admin":
                        session['Admin'] == True
                    if i == "Operator":
                        session['Operator'] == True
            return redirect(url_for('staff_options'))
        else:
            flash('Login unsuccesful, please check Username, Password, and Airline_name.', 'danger')
    return render_template('Staff_login.html', title='Login', form=form)
@app.route('/logout', methods=["GET", 'POST'])
def logout():
    # Remove session data, this will log the user out
    if session['type'] == 'customer':
        session.pop('loggedin', None)
        session.pop('email', None)
        session.pop('password', None)
        session.pop('type', None)
    elif session['type'] == 'agent':
        session.pop('loggedin', None)
        session.pop('email', None)
        session.pop('password', None)
        session.pop('type', None)
    elif session['type'] == 'staff':
        session.pop('loggedin', None)
        session.pop('username', None)
        session.pop('password', None)
        session.pop('airline', None)
        session.pop('type', None)
        if session['Admin']:
            session.pop('Admin', None)
        if session['Operator']:
            session.pop('Operator', None)

# Redirect to login page
    return redirect(url_for('home'))

@app.route('/customer_purchase', methods = ["GET", 'Post'])
def purchase():
    if session['loggedin'] == True and session['customer'] != None:
        with model.customer_connection.cursor(pymysql.cursors.DictCursor) as mycursor:
            query = 'Select max(ticket_id) from ticket'
            mycursor.execute(query)
            data = mycursor.fetchall()
            print(data)
            query = f"INSERT INTO ticket Values('{data[0]['max(ticket_id)'] + 1}','Jet Blue', 455)"
            mycursor.execute(query)
            model.customer_connection.commit()
            mycursor.close()

# @app.route('/staff_options', methods = ["GET", 'Post'])
# def staff_options():
#     # if session["Admin"]:
#     # if session['Operator']:
#     #
#     # return render_template('Layout.html', title='Home')
# if len(data) == 2:
#
# elif data[0] == 'Admin':
# elif data[0] == "Operator"
#
# query = f"INSERT INTO ticket Values('{data[0]['max(ticket_id)'] +1}','Jet Blue', 455)"
# mycursor.execute(query)
# model.staff_connection.commit()
# mycursor.close()






