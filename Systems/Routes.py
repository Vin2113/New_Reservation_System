from Reservation import app, bcrypt
from Forms import RegistrationForm, LoginForm, SearchForm, Booking_agent_LoginForm, Airline_staff_RegistrationForm, Airline_staff_LoginForm, Agent_RegistrationForm
from flask_login import login_user, current_user, logout_user, login_required
from flask import render_template, flash, redirect, session, request, url_for
import datetime
import model
import pymysql.cursors


@app.route('/')
@app.route('/home',methods=["GET","POST"])
def home():
    form = SearchForm()
    with model.connection.cursor(pymysql.cursors.DictCursor) as mycursor:
        mycursor.execute("SELECT * FROM airport ")
        depart = mycursor.fetchall()
        mycursor.execute("SELECT departure_time FROM available_flights")
        times = mycursor.fetchall()
        mycursor.close()
    depart.insert(0,{"airport_name":"Anywhere","airport_city":"Anywhere"})
    form.depart.choices = [(location["airport_city"] + ", " + location["airport_name"], location["airport_city"] + ", " + location["airport_name"])for location in depart]
    form.arrival.choices = [(location["airport_city"] + ", " + location["airport_name"], location["airport_city"] + ", " + location["airport_name"])for location in depart]
    return render_template('Home.html', title='Home', form=form)

@app.route('/search', methods = ["POST"])
def search():
    form=SearchForm()
    if form.validate_on_submit():
        depart = form.depart.data
        dest = form.arrival.data
        form.depart.choices = [(form.depart.data,form.depart.data)]
        form.arrival.choices = [(form.arrival.data,form.arrival.data)]
        l = depart.split(",")
        al = dest.split(",")
        departa = l[1].strip()
        desta = al[1].strip()
        if(departa != "Anywhere"):
            departa = "\'"+departa+"\'"
        else:
            departa = "departure_airport"
        if(desta != "Anywhere"):
            desta = "\'"+desta+"\'"
        else:
            desta = "arrival_airport"
        with model.connection.cursor(pymysql.cursors.DictCursor) as mycursor:
            mycursor.execute("SELECT * FROM available_flights WHERE departure_airport=" + departa)
            res = mycursor.fetchall()
            print(res)
            mycursor.close()
        
        return render_template('Search.html', title='Home', form=form, res=res)


@app.route('/register', methods=["GET", 'POST'])

def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        # #verify email unique
        #insert into database
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        phone_number = int(str(form.phone_number.data))
        email = str(form.email.data)
        exp_time = form.passport_expiration.data
        print(exp_time)
        dob_time = form.date_of_birth.data
        print(dob_time)
        #datetime.datetime(int(form.date_of_birth.data[-4:-1]), int(form.date_of_birth.data[0:2]), int(form.date_of_birth.data[3:5]))
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
            session['agent'] = account[0]
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
        session.pop('customer', None)
        session.pop('password', None)
        session.pop('type', None)
    elif session['type'] == 'agent':
        session.pop('loggedin', None)
        session.pop('agent', None)
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

@app.route('/customer_purchase', methods = ["GET", 'POST'])
def purchase():
    if session['loggedin'] == True and session['customer'] != None:
        #purchae and update
        with model.customer_connection.cursor(pymysql.cursors.DictCursor) as mycursor:
            query = 'Select max(ticket_id) from ticket'
            mycursor.execute(query)
            data = mycursor.fetchall()
            print(data)
            query = f"INSERT INTO ticket Values('{data[0]['max(ticket_id)'] + 1}','Jet Blue', 455)"
            mycursor.execute(query)
            model.customer_connection.commit()
            mycursor.close()

@app.route('/customer_profile', methods = ['GET', 'POST'])
def customer_account():
    #pulling spending
    with model.customer_connection.cursor(pymysql.cursors.DictCursor) as mycursor:
        query = f"Select sum(price) as spending "\
                "from flight inner join " \
                "Select * From purchases natural join ticket) as T on flight.flight_num = T.flight_num "\
                 f"Where customer_email = {session['customer']};"
        mycursor.execute(query)
        data = mycursor.fetchall()
        print(data)
        mycursor.close()

@app.route('/agent_profile', methods = ['GET', 'POST'])
def agent_account():

    # Booking Agent View for most recent 30 day commissions and number of tickets
    with model.agent_connection.cursor(pymysql.cursors.DictCursor) as mycursor:
        query_1 = "Select sum(price * .1) as commissions, count(ticket_id) as tickets from flight inner join(Select * From booking_agent natural join purchases natural join ticket) as T on flight.flight_num = T.flight_num Where purchase_date > Date_Sub(curdate(), INTERVAL 30 DAY) and email = 'Booking@agent.com';"
        mycursor.execute(query_1)
        data = mycursor.fetchall()
        mycursor.close()

    return render_template('agent_profile.html', data = data)

    # Booking Agent View for top 5 customers for 6 month by number
    #     query_2 = "Create View top_5_customer_by_number as" \
    #             "Select customer_email, count(ticket_id) as number_of_tickets" \
    #             "from flight inner join (Select * From booking_agent natural join purchases natural join ticket) as T on flight.flight_num = T.flight_num" \
    #             f"Where purchase_date > Date_Sub(curdate(), INTERVAL 6 MONTH) and email = {session['agent']}" \
    #             "group by customer_email" \
    #             "LIMIT 5;"

    # for 1 year commissions
    #     query_3 = f'''Create View top_5_customer_by_commission as
    #     Select customer_email, sum(price * .1) as commissions
    #     from flight inner join
    #     (Select *
    #     From booking_agent natural join purchases natural join ticket) as T on flight.flight_num = T.flight_num
    #     Where purchase_date > Date_Sub(curdate(), INTERVAL 1 YEAR) and email = {session['agent']}
    #     group by customer_email
    #     LIMIT 5;
    #     '''
    #     #data = mycursore.execute(query).fetchall()
    #     available_airlines =  mycursor.execute(f'''Select
    #     email, count(airline_name)
    #     from booking_agent_work_for
    #     where
    #     email = {session['agent']}''').fetchall()

# @app.route('/staff_profile', methods = ['GET', 'POST'])



