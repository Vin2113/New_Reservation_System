from Reservation import app, bcrypt
from Forms import RegistrationForm, LoginForm, SearchForm, Booking_agent_LoginForm, customerpurchaseForm, Airline_staff_RegistrationForm, Airline_staff_LoginForm, Agent_RegistrationForm, statuscheckForm, Staff_insert_airport_Form, Staff_grant_permission_Form, Staff_add_booking_agent_Form, Operator_Update_Flight_Form, add_flight_form

from flask_login import login_user, current_user, logout_user, login_required
from flask import render_template, flash, redirect, session, request, url_for
import datetime
from model import connection,staff_connection,agent_connection,customer_connection
import pymysql.cursors


@app.route('/')
@app.route('/home',methods=["GET","POST"])
def home():
    form = SearchForm()
    with connection.cursor(pymysql.cursors.DictCursor) as mycursor:
        mycursor.execute("SELECT * FROM airport ")
        depart = mycursor.fetchall()
        mycursor.close()
    depart.insert(0,{"airport_name":"Anywhere","airport_city":"Anywhere"})
    form.depart.choices = [(location["airport_city"] + ", " + location["airport_name"], location["airport_city"] + ", " + location["airport_name"])for location in depart]
    form.arrival.choices = [(location["airport_city"] + ", " + location["airport_name"], location["airport_city"] + ", " + location["airport_name"])for location in depart]
    return render_template('Home.html', title='Home', form=form)

@app.route('/statuscheck',methods=["GET","POST"])
def scheck():
    form = statuscheckForm()
    session.pop('status_search', None)
    if request.method == "POST":
        num = form.fnumber.data
        with connection.cursor(pymysql.cursors.DictCursor) as mycursor:
            mycursor.execute("SELECT status FROM available_flights where flight_num = " + '\'' + num + '\'')
            status = mycursor.fetchall()
            mycursor.close()
        session['status_search'] = status[0]['status']
    
    return render_template('statuscheck.html',title = 'statuscheck', form=form)


@app.route('/profile', methods=["GET","POST"])
def profile():
    if(session['type']==None):
        return redirect(url_for('home'))
    if(session['type'] == 'customer'):
        return redirect(url_for('profileCust',Username = session['username']))
    if(session['type'] == 'agent'):
        return redirect(url_for('profileAgent',Username = session['username']))
    if(session['type'] == 'staff'):
        return redirect(url_for('profileStf', Username = session['username']))
    

@app.route('/profile/<Username>', methods=["GET","POST"])
def profileCust(Username):
    with customer_connection.cursor(pymysql.cursors.DictCursor) as mycursor:
            query = f"select F.airline_name, F.flight_num, F.departure_airport, F.departure_time, F.arrival_airport, F.arrival_time, F.price, F.status, F.airplane_id, T.ticket_id from flight as F right join ticket as T on F.flight_num=T.flight_num right join (select * from purchases where customer_email = '{session['username']}') as P on T.ticket_id = P.ticket_id"
            mycursor.execute(query)
            history = mycursor.fetchall()
            session['history'] = history
            print(history)
            print(session['history'])
            mycursor.close()
    return render_template('Profile.html', title='Profile')

@app.route('/profileAgent/<Username>', methods=["GET","POST"])
def profileAgent(Username):
    session.pop('history',None)
    return render_template('Profile.html', title='')
        #with connection.cursor(pymysql.cursors.DictCursor) as mycursor:
            #mycursor.execute("SELECT ")
            #history = mycursor.fetchall()
            #mycursor.close()


@app.route('/profileStf/<Username>', methods=["GET","POST"])
def profileStf(Username):
    return render_template('Profile.html', title='')
        #with connection.cursor(pymysql.cursors.DictCursor) as mycursor:
            #mycursor.execute("SELECT ")
            #history = mycursor.fetchall()
            #mycursor.close()
        

@app.route('/search', methods = ["POST"])
def search():
    form=SearchForm()
    purchaseform=customerpurchaseForm()
    if request.method == "POST":
        if purchaseform.submit.data == True:
            if (session['type'] == 'agent'):
                return redirect(url_for(''))
            f_aln = request.form.get('tairlinen')
            f_num = request.form.get('tfnum')

            if session['loggedin'] == True and session['username'] != None:
            #purchase and update
                with customer_connection.cursor(pymysql.cursors.DictCursor) as mycursor:
                    query = 'Select max(ticket_id) from ticket'
                    mycursor.execute(query)
                    data = mycursor.fetchall()
                    print(data)
                    tid = data[0]['max(ticket_id)'] + 1
                    query = f"INSERT INTO ticket Values('{tid}','{f_aln}', {f_num})"
                    mycursor.execute(query)
                    customer_connection.commit()
                    query = f"INSERT INTO purchases Values('{tid}','{session['username']}', NULL ,'{datetime.datetime.now()}')"
                    mycursor.execute(query)
                    customer_connection.commit()
                    mycursor.close()
                return redirect(url_for('home'))
        depart = form.depart.data
        dest = form.arrival.data
        date = form.time.data
        if(date != "" and date !=None):
            dateandtime=date.split(',')
            date = dateandtime[0].strip()
            time = dateandtime[1].strip()
            date = date.split('/')
            time= time.split(':')
            dateandtime = datetime.datetime(int(date[2]),int(date[0]),int(date[1]),int(time[0]),int(time[1]))
            dateandtime = '\'' + str(dateandtime) + '\''
        else:
            dateandtime = "departure_time"
        form.depart.choices = [(form.depart.data,form.depart.data)]
        form.arrival.choices = [(form.arrival.data,form.arrival.data)]
        if(depart != None and dest != None):
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
        else:
            departa = "departure_airport"
            desta = "arrival_airport"
            
        with connection.cursor(pymysql.cursors.DictCursor) as mycursor:
            mycursor.execute("select * from available_flights where departure_airport =" + departa + " and arrival_airport ="+ desta +" and departure_time = " + dateandtime)
            res = mycursor.fetchall()
            mycursor.close()
                
        return render_template('Search.html', title='Home', form=form, res=res, purchaseform=purchaseform)


@app.route('/purchaseagent/<data>')
def purchaseagent(data):
    pdata= data
    print(data)
    return redirect(url_for('home'))

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
        dob_time = form.date_of_birth.data
        #datetime.datetime(int(form.date_of_birth.data[-4:-1]), int(form.date_of_birth.data[0:2]), int(form.date_of_birth.data[3:5]))
        query = f"Insert INTO customer VALUES('{email}', '{form.name.data}', '{hashed_password}','{form.building_number.data}','{form.street.data}','{form.city.data}','{form.state.data}', {phone_number} ,'{form.passport_number.data}','{exp_time}','{form.passport_country.data}','{dob_time}')"
        my_cursor = connection.cursor()
        my_cursor.execute(query)
        connection.commit()
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
        query = f"Insert INTO booking_agent VALUES('{email}', '{hashed_password}','{form.Id.data}')"
        my_cursor = connection.cursor()
        my_cursor.execute(query)
        connection.commit()
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
        my_cursor = connection.cursor()
        my_cursor.execute(query)
        connection.commit()
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
        my_cursor = connection.cursor()
        my_cursor.execute(query)
        account = my_cursor.fetchone()
        #checking user data from database for verification
        if account and bcrypt.check_password_hash(account[1],form.password.data):
            session['type'] = 'customer'
            session['loggedin'] = True
            session['username'] = account[0]
            session['password'] = account[1]
            flash('Login Successful', 'success')
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccesful, please check Email and Password.', 'danger')
    return render_template('Login.html', title='Login', form=form)

@app.route('/agent_login', methods=["GET", 'POST'])
def agent_login():
    form = Booking_agent_LoginForm()
    if form.validate_on_submit():
        str_email = str(form.email.data)
        id = str(form.Id.data)
        query = f"SELECT email, password, booking_agent_id from booking_agent WHERE email = '{str_email}'"
        my_cursor = connection.cursor()
        my_cursor.execute(query)
        account = my_cursor.fetchone()
        # checking user data from database for verification
        if account[0] == str_email and bcrypt.check_password_hash(account[1], form.password.data) and int(id) == account[2]:
            session['type'] = 'agent'
            session['loggedin'] = True
            session['username'] = account[0]
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
        my_cursor = connection.cursor()
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
            with staff_connection.cursor() as mycursor:
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
        session.pop('status_search', None)
        session.pop('history',None)
        session.pop('username', None)
        session.pop('password', None)
        session.pop('type', None)
    elif session['type'] == 'agent':
        session.pop('loggedin', None)
        session.pop('history',None)
        session.pop('username', None)
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

@app.route('/customer_profile', methods = ['GET', 'POST'])
def customer_account():
    #pulling spending
    with customer_connection.cursor(pymysql.cursors.DictCursor) as mycursor:
        query = f"Select sum(price) as spending "\
                "from flight inner join " \
                "Select * From purchases natural join ticket) as T on flight.flight_num = T.flight_num "\
                 f"Where customer_email = {session['username']};"
        mycursor.execute(query)
        data = mycursor.fetchall()
        print(data)
        mycursor.close()

@app.route('/agent_profile', methods = ['GET', 'POST'])
def agent_account():
    # Booking Agent View for most recent 30 day commissions and number of tickets
    with agent_connection.cursor(pymysql.cursors.DictCursor) as mycursor:
        query_1 = "Select sum(price * .1) as commissions, count(ticket_id) as tickets from flight inner join(Select * From booking_agent natural join purchases natural join ticket) as T on flight.flight_num = T.flight_num Where purchase_date > Date_Sub(curdate(), INTERVAL 30 DAY) and email = 'Booking@agent.com';"
        mycursor.execute(query_1)
        data = mycursor.fetchall()
        mycursor.close()
    return render_template('agent_profile.html', data = data)

    # Booking Agent View for top 5 customers for 6 month by number
    #     query_2 = "Create View top_5_customer_by_number as" \
    #             "Select customer_email, count(ticket_id) as number_of_tickets" \
    #             "from flight inner join (Select * From booking_agent natural join purchases natural join ticket) as T on flight.flight_num = T.flight_num" \
    #             f"Where purchase_date > Date_Sub(curdate(), INTERVAL 6 MONTH) and email = {session['username']}" \
    #             "group by customer_email" \
    #             "LIMIT 5;"

    # for 1 year commissions
    #     query_3 = f'''Create View top_5_customer_by_commission as
    #     Select customer_email, sum(price * .1) as commissions
    #     from flight inner join
    #     (Select *
    #     From booking_agent natural join purchases natural join ticket) as T on flight.flight_num = T.flight_num
    #     Where purchase_date > Date_Sub(curdate(), INTERVAL 1 YEAR) and email = {session['username']}
    #     group by customer_email
    #     LIMIT 5;
    #     '''
    #     #data = mycursor.execute(query).fetchall()
    #     available_airlines =  mycursor.execute(f'''Select
    #     email, count(airline_name)
    #     from booking_agent_work_for
    #     where
    #     email = {session['username']}''').fetchall()

@app.route('/staff_profile', methods = ['GET', 'POST'])
def staff_profile():
    # Query for all staffs
    # all flights within a staffs airline
    #query = f"SELECT * From flight WHERE airline_name = '{session['airline_name']}'"

    # View upcoming flights within the staffs airline by status
    #query_1 = f"SELECT * From flight WHERE airline_name = '{session['airline_name']}' and status = 'upcoming'"

    #view all customer of particular
    #query_2 = f"Select customer_email From ticket natural join purchases Where airline_name = '{session['airline_name']}' and flight_num = '{input_flight_num}'

    # See all flights taken by a certain customer
    #query_3 = f"Select flight_num From ticket natural join purchases Where airline_name = '{session['airline_name']}' and customer_email = {input_customer_email}

    #Reports of of tickets sold
    #Amount of tickets sold in a month
    #query_4 = f"Select count(ticket_id) From ticket natural join purchases Where airline_name = session[airline_name] group by customer_email Where purchase_date > Date_Sub(curdate(), INTERVAL 30 DAY) and airline_name = {airline_name}; Limit 1;"

    # Most Frequent customer
    #query_5 = f"Select customer_email, count(ticket_id) From ticket natural join purchases Where airline_name = '{session['airline_name']}' group by customer_email Limit 1;"


    #Admin Queries
    #New Airplane

    query_5 = f"Insert into airplane Values('{session['airline_name']}', airplane_id, seats)"

    #Insert flight into flights
    query_6 =f"Insert into flight Values('{session['airline_name']}', flight_number, departure_airport, departure_time, arrival_airport, arrival_time, price, status, airplane_id)"

@app.route('/admin_insert_airport', methods=['GET', 'POST'])
def admin_insert_airport():
    form = Staff_insert_airport_Form()
    if form.validate_on_submit():
    #Admin insert airport for airline
        with staff_connection.cursor(pymysql.cursors.DictCursor) as mycursor:
            str_airport_name = str(form.airport_name.data)
            query = f"Select airport_name from airport where airport_name = '{str_airport_name}' "
            mycursor.execute(query)
            data = mycursor.fetchall()
            mycursor.close()
        if not data:
            str_aiport_city = str(form.airport_city.data)
            with staff_connection.cursor(pymysql.cursors.DictCursor) as mycursor:
                query = f"Insert into airport Values('{str_airport_name}', '{str_aiport_city}')"
                mycursor.execute(query)
                mycursor.close()
                staff_connection.commit()
        with staff_connection.cursor(pymysql.cursors.DictCursor) as mycursor:
            str_airport_name = form.airport_name.data
            query = f"Insert into airline_available_airports Values('Jet Blue', '{str_airport_name}')"
            mycursor.execute(query)
            staff_connection.commit()
            mycursor.close()
            #Search for customer on a flight
        flash('Added Airport', 'success')
        return redirect(url_for('home'))
    return render_template('insert_airport.html', form=form)

@app.route('/admin_grant_permission', methods=['GET', 'POST'])
def grant_permission():
    form = Staff_grant_permission_Form()
    if form.validate_on_submit():
        # Admin insert airport for airline
        with staff_connection.cursor(pymysql.cursors.DictCursor) as mycursor:
            str_username = str(form.username.data)
            str_status = str(form.status.data)
            query = f"Insert into permission Values('{str_username}', '{str_status}')"
            mycursor.execute(query)
            staff_connection.commit()
            mycursor.close()
        flash('Permission Granted', 'success')
        # return redirect(url_for('home'))
    return render_template('staff_grant_permission.html', form=form)

@app.route('/add_booking_agent', methods=['GET', 'POST'])
def add_booking_agent():
    form = Staff_add_booking_agent_Form()
    # Admin insert airport for airline
    if form.validate_on_submit():
        with staff_connection.cursor(pymysql.cursors.DictCursor) as mycursor:
            str_email = str(form.email.data)
            query = f"Insert into booking_agent_work_for Values('{str_email}', 'Jet Blue')"
            mycursor.execute(query)
            staff_connection.commit()
            mycursor.close()
        flash('Agent Added', 'success')
        return redirect(url_for('home'))

    return render_template('staff_add_booking_agent.html', form=form)

# @app.route('/add_flight', methods=['GET', 'POST'])
# def add_flight():
#     form = add_flight_form()
#     if form.validate_on_submit():

#operater use case
@app.route('/update_flight', methods=['GET', 'POST'])
def update_flight():
    form = Operator_Update_Flight_Form()
    if form.validate_on_submit():
        with staff_connection.cursor(pymysql.cursors.DictCursor) as mycursor:
            str_flight_status = str(form.flight_status.data)
            str_flight_num = str(form.flight_num.data)
            query = f"UPDATE flight SET status = '{str_flight_status}' WHERE flight_num = '{str_flight_num}';"
            mycursor.execute(query)
            staff_connection.commit()
            mycursor.close()







