from sre_constants import SUCCESS
from Reservation import app, bcrypt
from Forms import RegistrationForm, LoginForm, SearchForm, Booking_agent_LoginForm, customerpurchaseForm, Airline_staff_RegistrationForm, Airline_staff_LoginForm, Agent_RegistrationForm, statuscheckForm, Staff_insert_airport_Form, Staff_grant_permission_Form, Staff_add_booking_agent_Form, Operator_Update_Flight_Form, add_flight_form,rangeForm,airplaneForm
from dateutil.rrule import rrule, MONTHLY
from flask_login import login_user, current_user, logout_user, login_required
from flask import render_template, flash, redirect, session, request, url_for
from datetime import date,datetime
from dateutil.relativedelta import relativedelta
from model import connection,staff_connection,agent_connection,customer_connection
import pymysql.cursors

def monthspan(startDate, endDate, delta=relativedelta(months=1)):
    currentDate = startDate
    while currentDate > endDate:
        yield currentDate
        currentDate -= delta
    

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
        return redirect(url_for('agent_account',username=session['username']))
    if(session['type'] == 'staff'):
        return redirect(url_for('staff_profile', username=session['username']))
    

@app.route('/profile/<Username>', methods=["GET","POST"])
def profileCust(Username):
    form = rangeForm()
    session.pop('data',None)
    data={}
    with customer_connection.cursor(pymysql.cursors.DictCursor) as mycursor:
            query = f"select F.airline_name, F.flight_num, F.departure_airport, F.departure_time, F.arrival_airport, F.arrival_time, F.price, F.status, F.airplane_id, T.ticket_id from flight as F right join ticket as T on F.flight_num=T.flight_num right join (select * from purchases where customer_email = '{session['username']}') as P on T.ticket_id = P.ticket_id"
            mycursor.execute(query)
            history = mycursor.fetchall()
            data['history'] = history
            query = f"select sum(F.price) from flight as F left join ticket as T on T.flight_num = F.flight_num left join purchases as P on T.ticket_id = P.ticket_id where P.customer_email = '{session['username']}' and p.purchase_date > date_sub(curdate(), INTERVAL 1 Year)"
            mycursor.execute(query)
            soney = mycursor.fetchone()
            data['oneyear'] = soney
            query = f"select monthname(P.purchase_date) as month, year(P.purchase_date) as year, sum(F.price) as spending from flight as F left join ticket as T on F.flight_num = T.flight_num right join purchases as P on T.ticket_id = P.ticket_id  where P.customer_email = '{session['username']}' and p.purchase_date > date_sub(curdate(), INTERVAL 6 month) group by month(P.purchase_date)"
            mycursor.execute(query)
            mdata= mycursor.fetchall()
            data['mdata'] = mdata
            mycursor.close()
    now = datetime.now()
    sixm = now - relativedelta(months=6)
    label = []
    ldata = []
    span=[]
    dataspan= []
    datamod = []
    for t in monthspan(now, sixm):
        temp = t.strftime("%Y")+ ", " +t.strftime("%B")
        span.append(temp)    
    for d in data['mdata']:
        datamod.append({'months':str(d['year'])+", " + d['month'], 'value':int(d['spending'])})
        dataspan.append(str(d['year'])+", " + d['month'])
    print(datamod)
    for x in span:
        if x not in dataspan:
            label.append(x)
            ldata.append(0)
        else:
            for y in datamod:
                if y['months'] == x:
                    label.append(x)
                    ldata.append(y['value'])
    print(label)
    print(ldata)
    data['label'] = label
    data['ldata'] = ldata
    session['data'] = data
    if request.method=="POST":
        dateone = form.dateone.data
        datetwo = form.datetwo.data
        data['dates'] = [dateone, datetwo]
        session['data'] = data
        return redirect(url_for('rangesearch',username = session['username'], datef = dateone, dates = datetwo))
         
    
    return render_template('Profile.html', title='Profile', form=form)

@app.route('/profile/<username>/<datef>to<dates>')
def rangesearch(username,datef,dates):
    with customer_connection.cursor(pymysql.cursors.DictCursor) as mycursor:
        query = f"select monthname(P.purchase_date) as month, year(P.purchase_date) as year, sum(F.price) as spending from flight as F left join ticket as T on F.flight_num = T.flight_num right join purchases as P on T.ticket_id = P.ticket_id  where P.customer_email = '{session['username']}' and P.purchase_date <= '{datef}' AND P.purchase_date >='{dates}' group by month(P.purchase_date),year(P.purchase_date)"
        mycursor.execute(query)
        mdata= mycursor.fetchall()
        query = f"select sum(F.price) as spending from flight as F left join ticket as T on F.flight_num = T.flight_num right join purchases as P on T.ticket_id = P.ticket_id  where P.customer_email = '{session['username']}' and P.purchase_date <= '{datef}' AND P.purchase_date >='{dates}'"
        mycursor.execute(query)
        sumoney = mycursor.fetchall()
        mycursor.close()
    datef = datef.split('-')
    dates = dates.split('-')
    datef = datetime(int(datef[0]), int(datef[1]), int(datef[2]))
    dates = datetime(int(dates[0]),int(dates[1]),int(dates[2]))
    label = []
    ldata = []
    span=[]
    dataspan= []
    datamod = []
    sumoney = sumoney[0]['spending']
    for t in monthspan(datef, dates):
        temp = t.strftime("%Y")+ ", " +t.strftime("%B")
        span.append(temp)    
    for d in mdata:
        datamod.append({'months':str(d['year'])+", " + d['month'], 'value':int(d['spending'])})
        dataspan.append(str(d['year'])+", " + d['month'])
    print(datamod)
    for x in span:
        if x not in dataspan:
            label.append(x)
            ldata.append(0)
        else:
            for y in datamod:
                if y['months'] == x:
                    label.append(x)
                    ldata.append(y['value'])
    print(label)
    print(ldata)
    return render_template('Crangesearch.html', title='Rangesearch', label=label, ldata=ldata, sumoney = sumoney)

@app.route('/search', methods = ["POST"])
def search():
    form=SearchForm()
    purchaseform=customerpurchaseForm()
    if request.method == "POST":
        if purchaseform.submit.data == True:
            if (session['type'] == 'agent'):
                data = {}
                data['customeremail']=request.form.get('customeremail')
                data['customerpass']=request.form.get('customerpass')
                data['cusname']=request.form.get('cusname')
                data['bnum']=request.form.get('bnum')
                data['st']=request.form.get('st')
                data['city']=request.form.get('city')
                data['state']=request.form.get('state')
                data['pnum']=request.form.get('pnum')
                data['pasnum']=request.form.get('pasnum')
                data['pexp']=request.form.get('pexp')
                data['pcoun']=request.form.get('pcoun')
                data['dob']=request.form.get('dob')
                data['tairlinen']=request.form.get('tairlinen')
                data['tfnum']=request.form.get('tfnum')
                session['data'] = data
                return redirect(url_for('purchaseagent', pdata=data))
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
                    query = f"INSERT INTO purchases Values('{tid}','{session['username']}', NULL ,'{datetime.now()}')"
                    mycursor.execute(query)
                    customer_connection.commit()
                    mycursor.close()
                flash(f'Ticket Purchased!', 'success')
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
            dateandtime = datetime(int(date[2]),int(date[0]),int(date[1]),int(time[0]),int(time[1]))
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


@app.route('/purchaseagent/<pdata>')
def purchaseagent(pdata):
    with agent_connection.cursor(pymysql.cursors.DictCursor) as my_cursor:    
        query = f"select email from customer where email = '{session['data']['customeremail']}'"
        my_cursor.execute(query)
        cust = my_cursor.fetchone()
        hashed_password = bcrypt.generate_password_hash(session['data']['customerpass']).decode('utf-8')  
        if cust is None:
            expd = session['data']['pexp'].split('-')
            expd = datetime(int(expd[0]),int(expd[1]),int(expd[2]))
            dob = session['data']['dob'].split('-')
            dob = datetime(int(dob[0]),int(dob[1]),int(dob[2]))
            query = f"Insert INTO customer VALUES('{session['data']['customeremail']}','{session['data']['cusname']}','{hashed_password}','{session['data']['bnum']}','{session['data']['st']}','{session['data']['city']}','{session['data']['state']}', {int(session['data']['pnum'])} ,'{session['data']['pasnum']}', '{expd}' ,'{session['data']['pcoun']}','{dob}')"
            my_cursor.execute(query)    
        query = 'Select max(ticket_id) from ticket'
        my_cursor.execute(query)
        data = my_cursor.fetchall()
        print(data)
        tid = data[0]['max(ticket_id)'] + 1
        query = f"INSERT INTO ticket Values('{tid}','{session['data']['tairlinen']}', {session['data']['tfnum']})"
        my_cursor.execute(query)
        query = f"INSERT INTO purchases Values('{tid}','{session['data']['customeremail']}', {session['id']} ,'{datetime.now()}')"
        my_cursor.execute(query)
        agent_connection.commit()
        my_cursor.close()
        session.pop('data',None)
    flash(f"Ticket has been purchased!", 'success')
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
        with customer_connection.cursor()as my_cursor:
            query = f"Insert INTO customer VALUES('{email}', '{form.name.data}', '{hashed_password}','{form.building_number.data}','{form.street.data}','{form.city.data}','{form.state.data}', {phone_number} ,'{form.passport_number.data}','{exp_time}','{form.passport_country.data}','{dob_time}')"
            my_cursor.execute(query)
            customer_connection.commit()
            my_cursor.close()
        flash(f'You can now login {form.name.data}!', 'success')
        return redirect(url_for('login'))
    return render_template('Register.html', title='Register', form=form)


@app.route('/agent_register', methods=["GET", 'POST'])
def agent_register():
    form = Agent_RegistrationForm()
    if form.validate_on_submit():
        with agent_connection.cursor(pymysql.cursors.DictCursor) as my_cursor:
            # #verify email unique
            #insert into database
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            email = str(form.email.data)
            query = f"SELECT Max(booking_agent_id) as max From booking_agent"
            my_cursor.execute(query)
            data = my_cursor.fetchone()
            new_id = str(int(data['max']) + 1)
            query = f"Insert INTO booking_agent VALUES('{email}', '{hashed_password}','{new_id}')"
            my_cursor.execute(query)
            agent_connection.commit()
            my_cursor.close()
            flash(f'You can now login {form.email.data}, you Agent ID will be {new_id}!', 'success')
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
        dob_time = form.date_of_birth.data
        first_name = str(form.first_name.data)
        last_name = str(form.last_name.data)
        airline_name = str(form.airline_name.data)
        with staff_connection.cursor() as my_cursor:
            query = f"Insert INTO airline_staff VALUES('{username}', '{hashed_password}','{first_name}','{last_name}', '{dob_time}', '{airline_name}')"
            my_cursor.execute(query)
            staff_connection.commit()
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
        with customer_connection.cursor() as my_cursor:
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
        with agent_connection.cursor() as my_cursor:
            str_email = str(form.email.data)
            str_id = str(form.Id.data)
            print(str_email)
            print(str_id)
            query = f"SELECT email, password, booking_agent_id from booking_agent WHERE email = '{str_email}'"
            my_cursor.execute(query)
            account = my_cursor.fetchone()
            query = f"Select email, airline_name from booking_agent_work_for where email = '{str_email}'"
            my_cursor.execute(query)
            aline = my_cursor.fetchall()
            my_cursor.close()
            # checking user data from database for verification
            if (account == None):
                flash('Login unsuccesful, please check Email, Password, and ID.', 'danger')
                return redirect(url_for('home'))
            if account[0] == str_email and bcrypt.check_password_hash(account[1], form.password.data) and int(str_id) == account[2]:
                data=[]
                if(aline == None):
                    data.append('NONE')
                for i in aline:
                    data.append(i[1])
                session['type'] = 'agent'
                session['loggedin'] = True
                session['username'] = account[0]
                session['password'] = account[1]
                session['id'] = account[2]
                session['alines'] = data
                session['comdatas'] = None
                flash('Login Successful', 'success')
                return redirect(url_for('home'))
            else:
                flash('Login unsuccesful, please check Email, Password, and ID.', 'danger')
    return render_template('Agent_login.html', title='Login', form=form)

@app.route('/staff_login', methods=["GET", 'POST'])
def staff_login():
    form = Airline_staff_LoginForm()
    if form.validate_on_submit():
        with staff_connection.cursor() as mycursor:
            str_username = str(form.username.data)
            str_airline_name = str(form.airline_name.data)
            query = f"SELECT username, password From airline_staff  WHERE username = '{str_username}' and airline_name = '{str_airline_name}'"
            mycursor.execute(query)
            account = mycursor.fetchone()
            # checking user data from database for verification
            if account is None:
                flash('Login unsuccesful, please check Username, Password, and Airline_name.', 'danger')
            elif account[0] == str_username and bcrypt.check_password_hash(account[1], form.password.data):
                query = f"SELECT permission_type From permission WHERE username = '{str_username}'"
                mycursor.execute(query)
                data = mycursor.fetchall()
                for i in data:
                    if i[0] == "Admin":
                        session['Admin'] = True
                    if i[0] == "Operator":
                        session['Operator'] = True
                session['type'] = 'staff'
                session['loggedin'] = True
                session['username'] = account[0]
                session['password'] = account[1]
                session['airline_name'] = str_airline_name
                flash('Login Successful', 'success')
                mycursor.close()
                return redirect(url_for('home'))
            else:
                flash('Login Unsuccesful, please check Email and Password.', 'danger')
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
        session.pop('data',None)
        session.pop('type', None)
    elif session['type'] == 'agent':
        session.pop('loggedin', None)
        session.pop('history',None)
        session.pop('username', None)
        session.pop('password', None)
        session.pop('id', None)
        session.pop('data',None)
        session.pop('aline',None)
        session.pop('comdatas', None)
        session.pop('type', None)
    elif session['type'] == 'staff':
        session.pop('loggedin', None)
        session.pop('username', None)
        session.pop('password', None)
        session.pop('airline_name', None)
        session.pop('type', None)
        session.pop('Admin', None)
        session.pop('dates',None)
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

@app.route('/profileAgent/<username>', methods = ['GET', 'POST'])
def agent_account(username):
    form = rangeForm()
    # Booking Agent View for most recent 30 day commissions and number of tickets
    session.pop('comdatas', None)
    with agent_connection.cursor(pymysql.cursors.DictCursor) as mycursor:
        query = f"Select sum(price * .1) as commissions, count(ticket_id) as tickets from flight inner join(Select * From booking_agent natural join purchases natural join ticket) as T on flight.flight_num = T.flight_num Where purchase_date > Date_Sub(curdate(), INTERVAL 30 DAY) and email = '{session['username']}';"
        mycursor.execute(query)
        sumcomthirty = mycursor.fetchall()
        query = f"select F.airline_name, F.flight_num, F.departure_airport, F.departure_time, F.arrival_airport, F.arrival_time, F.price, F.status, P.customer_email from flight as F left join ticket as T on F.flight_num = T.flight_num left join purchases as P on T.ticket_id = P.ticket_id left join booking_agent as B on P.booking_agent_id = B.booking_agent_id where B.email = '{session['username']}'"
        mycursor.execute(query)
        phist = mycursor.fetchall()
        query = f"Select customer_email, count(ticket_id) as number_of_tickets from flight inner join (Select * From booking_agent natural join purchases natural join ticket) as T on flight.flight_num = T.flight_num Where purchase_date > Date_Sub(curdate(), INTERVAL 6 MONTH) and email = '{session['username']}' group by customer_email LIMIT 5;"
        mycursor.execute(query)
        tfct = mycursor.fetchall()
        query = f"Select customer_email, sum(price * .1) as commissions from flight inner join (Select * From booking_agent natural join purchases natural join ticket) as T on flight.flight_num = T.flight_num Where purchase_date > Date_Sub(curdate(), INTERVAL 1 YEAR) and email = '{session['username']}' group by customer_email LIMIT 5;"
        mycursor.execute(query)
        tfcc = mycursor.fetchall()
        mycursor.close()
    
    tlabels = [i['customer_email'] for i in tfct]
    clabels = [i['customer_email'] for i in tfcc]
    tdata = [i['number_of_tickets'] for i in tfct]
    cdata = [float(i['commissions']) for i in tfcc]
    print(sumcomthirty)
    if request.method == "POST":
            fdate = form.dateone.data
            sdate = form.datetwo.data
            with agent_connection.cursor(pymysql.cursors.DictCursor) as mycursor:
                query = f"Select sum(price * .1) as commissions, count(ticket_id) as tickets from flight inner join(Select * From booking_agent natural join purchases natural join ticket) as T on flight.flight_num = T.flight_num Where purchase_date <= '{fdate}' AND purchase_date >='{sdate}' and email = '{session['username']}'"
                mycursor.execute(query)
                rangecom = mycursor.fetchall()
            comdatas = []
            comdatas.append(rangecom[0]['commissions'])
            comdatas.append(rangecom[0]['tickets'])
            session['comdatas'] = comdatas
                
            
            
            
    return render_template('agent_profile.html', form = form, title=username, sumcomthirty = sumcomthirty, phist=phist, tfct=tfct, tfcc = tfcc, tlabels = tlabels, tdata=tdata, clabels=clabels, cdata=cdata)

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

@app.route('/staff_profile/<username>', methods = ['GET', 'POST'])
def staff_profile(username):
    staffdata={}
    session['dates'] = None
    form = rangeForm()
    with staff_connection.cursor(pymysql.cursors.DictCursor) as mycursor:
        query = f"SELECT * From flight WHERE airline_name = '{session['airline_name']}'"
        mycursor.execute(query)
        staffdata['flights'] = mycursor.fetchall()
        query = f"Select customer_email, count(ticket_id) From ticket natural join purchases Where airline_name = '{session['airline_name']}' group by customer_email Limit 1;"
        mycursor.execute(query)
        staffdata['freqcus'] = mycursor.fetchone()
        query = f"select sum(F.price) as total from flight as F right join ticket as T on T.flight_num = F.flight_num right join purchases as P on P.ticket_id = T.ticket_id where P.booking_agent_id is null and T.airline_name = '{session['airline_name']}' and purchase_date > date_sub(curdate(), interval 30 day)"
        mycursor.execute(query)
        directt = mycursor.fetchone()
        staffdata['directt'] = directt
        query = f"select sum(F.price) as total from flight as F right join ticket as T on T.flight_num = F.flight_num right join purchases as P on P.ticket_id = T.ticket_id where P.booking_agent_id is not null and T.airline_name = '{session['airline_name']}' and purchase_date > date_sub(curdate(), interval 30 day)"
        mycursor.execute(query)
        indirectt = mycursor.fetchone()
        staffdata['indirectt'] = indirectt
        query = f"select sum(F.price) as total from flight as F right join ticket as T on T.flight_num = F.flight_num right join purchases as P on P.ticket_id = T.ticket_id where P.booking_agent_id is null and T.airline_name = '{session['airline_name']}' and purchase_date > date_sub(curdate(), interval 1 year)"
        mycursor.execute(query)
        directy = mycursor.fetchone()
        staffdata['directy'] = directy
        query = f"select sum(F.price) as total from flight as F right join ticket as T on T.flight_num = F.flight_num right join purchases as P on P.ticket_id = T.ticket_id where P.booking_agent_id is not null and T.airline_name = '{session['airline_name']}' and purchase_date > date_sub(curdate(), interval 1 year)"
        mycursor.execute(query)
        indirecty = mycursor.fetchone()
        staffdata['indirecty'] = indirecty
    if request.method=="POST":
        datef = form.dateone.data
        dates = form.datetwo.data
        return redirect(url_for('staffcharts',datef = datef, dates=dates))
    
    return render_template('staff_profile.html', title = session['username'],form = form, staffdata=staffdata)

@app.route('/staffchartrange/<datef>to<dates>', methods = ['GET', 'POST'])
def staffcharts(datef, dates):
    print(datef)
    print(dates)
    datef = datef.split('-')
    dates = dates.split('-')
    datef = datetime(int(datef[0]), int(datef[1]), int(datef[2]))
    dates = datetime(int(dates[0]), int(dates[1]), int(dates[2]))
    with staff_connection.cursor(pymysql.cursors.DictCursor) as mycursor:
        query = f"select monthname(purchase_date) as month, year(purchase_date) as year, count(purchases.ticket_id) as sales from purchases join ticket natural join flight where flight.airline_name = '{session['airline_name']}' and purchase_date <= '{datef}' AND purchase_date >='{dates}'group by month(purchase_date),year(purchase_date)"
        mycursor.execute(query)
        numbers= mycursor.fetchall()
        print(numbers)
    label = []
    ldata = []
    span=[]
    dataspan= []
    datamod = []
    for t in monthspan(datef, dates):
        temp = t.strftime("%Y")+ ", " +t.strftime("%B")
        span.append(temp)    
    for d in numbers:
        datamod.append({'months':str(d['year'])+", " + d['month'], 'value':int(d['sales'])})
        dataspan.append(str(d['year'])+", " + d['month'])
    print(datamod)
    for x in span:
        if x not in dataspan:
            label.append(x)
            ldata.append(0)
        else:
            for y in datamod:
                if y['months'] == x:
                    label.append(x)
                    ldata.append(y['value'])
    print(label)
    print(ldata)
    return render_template('staff_charts.html', title = session['username'] +'chart', label =label, ldata=ldata)

@app.route('/top_agent_by_sales_1month', methods=['GET', 'POST'])
def top_agent_by_sales_1month():
    session.pop('data', None)
    idata = {}
    with staff_connection.cursor(pymysql.cursors.DictCursor) as mycursor:
        query = f"Select email, count(ticket_id) as sales from (select email, booking_agent_id from booking_agent natural join booking_agent_work_for where airline_name = '{session['airline_name']}') as T join purchases on T.booking_agent_id = purchases.booking_agent_id natural join ticket natural join flight  Where purchase_date > Date_Sub(curdate(), INTERVAL 30 DAY) group by email order by sales DESC Limit 5"
        mycursor.execute(query)
        data = mycursor.fetchall()
        session['data'] = data
        email = []
        sales = []
        for i in data:
            email.append(i['email'])
            sales.append(i['sales'])
        idata['agent_emails'] = email
        idata['agent_sales'] = sales
        idata['data'] = data
    session['data'] = idata

    return render_template('top_agent_by_sales.html')

@app.route('/top_agent_by_sales_1year', methods=['GET', 'POST'])
def top_agent_by_sales_1year():
    session.pop('data', None)
    idata = {}
    with staff_connection.cursor(pymysql.cursors.DictCursor) as mycursor:
        query = f"Select email, count(ticket_id) as sales from (select email, booking_agent_id from booking_agent natural join booking_agent_work_for where airline_name = '{session['airline_name']}') as T join purchases on T.booking_agent_id = purchases.booking_agent_id natural join ticket natural join flight  Where purchase_date > Date_Sub(curdate(), INTERVAL 1 YEAR) group by email order by sales DESC Limit 5"
        mycursor.execute(query)
        data = mycursor.fetchall()
        session['data'] = data
        email = []
        sales = []
        for i in data:
            email.append(i['email'])
            sales.append(i['sales'])
        idata['agent_emails'] = email
        idata['agent_sales'] = sales
        idata['data'] = data
    session['data'] = idata

    return render_template('top_agent_by_sales.html')


@app.route('/top_agent_by_commissions', methods=['GET', 'POST'])
def top_agent_by_commissions():
    session.pop('data', None)
    idata = {}
    with staff_connection.cursor(pymysql.cursors.DictCursor) as mycursor:
        query = f"Select email, sum(price * .1) as commissions from (select email, booking_agent_id from booking_agent natural join booking_agent_work_for where airline_name = '{session['airline_name']}') as T join purchases on T.booking_agent_id = purchases.booking_agent_id natural join ticket natural join flight  Where purchase_date > Date_Sub(curdate(), INTERVAL 1 YEAR) group by email order by commissions DESC Limit 5"
        mycursor.execute(query)
        data = mycursor.fetchall()
        session['data'] = data
        email = []
        commissions = []
        for i in data:
            email.append(i['email'])
            commissions.append(float(i['commissions']))
        idata['agent_emails'] = email
        idata['agent_commissions'] = commissions
        idata['data'] = data
    session['data'] = idata

    return render_template('top_agent_by_commissions.html')

@app.route('/top_destination_3month', methods=['GET', 'POST'])
def top_destination_3month():
    session.pop('data', None)
    idata = {}
    with staff_connection.cursor(pymysql.cursors.DictCursor) as mycursor:
        query = f"SELECT arrival_airport as destination, count(ticket_id) as count FROM purchases natural join flight Where purchase_date > Date_Sub(curdate(), INTERVAL 3 MONTH) and airline_name = '{session['airline_name']}' group by arrival_airport order by count(ticket_id) DESC Limit 3"
        mycursor.execute(query)
        data = mycursor.fetchall()
        session['data'] = data
        destinations = []
        count = []
        for i in data:
            destinations.append(i['destination'])
            count.append(i['count'])
        idata['destination'] = destinations
        idata['count'] = count
        idata['data'] = data
    session['data'] = idata

    return render_template('top_destination.html')
@app.route('/top_destination_1year', methods=['GET', 'POST'])
def top_destination_1year():
    session.pop('data', None)
    idata = {}
    with staff_connection.cursor(pymysql.cursors.DictCursor) as mycursor:
        query = f"SELECT arrival_airport as destination, count(ticket_id) as count FROM purchases natural join flight Where purchase_date > Date_Sub(curdate(), INTERVAL 1 YEAR) and airline_name = '{session['airline_name']}' group by arrival_airport order by count(ticket_id) DESC Limit 3"
        mycursor.execute(query)
        data = mycursor.fetchall()
        session['data'] = data
        destinations = []
        count = []
        for i in data:
            destinations.append(i['destination'])
            count.append(i['count'])
        idata['destination'] = destinations
        idata['count'] = count
        idata['data'] = data
    session['data'] = idata

    return render_template('top_destination.html')

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
            query = f"Select airport_name from airline_available_airports where airport_name = '{str_airport_name}' and airline_name = '{session['airline_name']}'"
            mycursor.execute(query)
            data = mycursor.fetchall()
            if data:
                flash('Aiport Already Added', 'danger')
                return redirect(request.url)
            query = f"Insert into airline_available_airports Values('{session['airline_name']}', '{str_airport_name}')"
            mycursor.execute(query)
            staff_connection.commit()
            mycursor.close()
        flash('Added Airport', 'success')
        return redirect(url_for('staff_profile', username=session['username']))
    return render_template('insert_airport.html', form=form)

@app.route('/admin_grant_permission', methods=['GET', 'POST'])
def grant_permission():
    form = Staff_grant_permission_Form()
    if form.validate_on_submit():
        # Admin insert airport for airline
        with staff_connection.cursor(pymysql.cursors.DictCursor) as mycursor:
            str_username = str(form.username.data)
            str_status = str(form.status.data)
            query = f"Select username from airline_staff where username = '{str_username}' and airline_name = '{session['airline_name']}'"
            mycursor.execute(query)
            data = mycursor.fetchone()
            if data is None:
                flash('User is not a staff, Pleas type in the right username', 'danger')
                return redirect(request.url)
            else:
                query = f"Select username from permission where username = '{str_username}' AND permission_type = '{str_status}'"
                mycursor.execute(query)
                data = mycursor.fetchall()
                if data:
                    flash('User already have this permission', 'danger')
                    return redirect(request.url)
                else:
                    query = f"Insert into permission Values('{str_username}', '{str_status}')"
                    mycursor.execute(query)
                    staff_connection.commit()
                mycursor.close()
                flash('Permission Granted', 'success')
                return redirect(url_for('staff_profile', username=session['username']))

    return render_template('staff_grant_permission.html', form=form)

@app.route('/add_booking_agent', methods=['GET', 'POST'])
def add_booking_agent():
    form = Staff_add_booking_agent_Form()
    # Admin insert airport for airline
    if form.validate_on_submit():
        with staff_connection.cursor(pymysql.cursors.DictCursor) as mycursor:
            str_email = str(form.email.data)
            query = f"Select email from booking_agent_work_for where email = '{str_email}' and airline_name =  '{session['airline_name']}'"
            mycursor.execute(query)
            data = mycursor.fetchone()
            mycursor.close()
            if data:
                flash('Agent Already Added', 'danger')
                return redirect(request.url)
            else:
                with staff_connection.cursor(pymysql.cursors.DictCursor) as mycursor:
                    str_email = str(form.email.data)
                    query = f"Insert into booking_agent_work_for Values('{str_email}', '{session['airline_name']}')"
                    mycursor.execute(query)
                    staff_connection.commit()
                    mycursor.close()
                flash('Agent Added', 'success')
                return redirect(url_for('staff_profile', username=session['username']))
    return render_template('staff_add_booking_agent.html', form=form)

@app.route('/add_flight', methods=['GET', 'POST'])
def add_flight():
    form = add_flight_form()
    if form.validate_on_submit():
        if form.dep_time.data > form.arr_time_name.data:
            flash("Check departure time", 'danger')
            return redirect(url_for('add_flight'))
        with staff_connection.cursor(pymysql.cursors.DictCursor) as mycursor:
            query = f"Select airport_name from airline_available_airports where airline_name = '{session['airline_name']}'"
            mycursor.execute(query)
            str_dep_airport = str(form.dep_airport_name.data)
            str_arr_airport = str(form.arr_airport_name.data)
            if str_arr_airport == str_dep_airport:
                flash('Airports are the same', 'danger')
            data = mycursor.fetchall()
            lst = []
            for i in data:
                lst.append(i['airport_name'])
            if str_dep_airport not in lst:
                flash("Invalid Departure Airport", 'danger')
                return redirect(url_for('add_flight'))
            if str_arr_airport not in lst:
                flash("Invalid Arrival Airport", 'danger')
                return redirect(url_for('add_flight'))
            query = f'Select Max(flight_num) as max_number from flight'
            mycursor.execute(query)
            data = mycursor.fetchone()
            new_flight_number = str(data['max_number'] + 1)

            str_status = str(form.status.data)
            str_price = str(form.price.data)
            str_airplane_id = str(form.airplane_id.data)
            dep_time = form.dep_time.data
            arr_time = form.arr_time.data
            query = f"Insert into flight Values('{session['airline_name']}', {new_flight_number}, '{str_dep_airport}','{dep_time}','{str_arr_airport}','{arr_time}',{str_price},'{str_status}', {str_airplane_id})"
            mycursor.execute(query)
            staff_connection.commit()
            mycursor.close()
            flash('flight added', 'success')
            return redirect(url_for('staff_profile', username=session['username']))

        flash('unSuccesful', 'danger')
        return redirect(url_for('add_flight'))
    return render_template('add_flight.html', form = form)

@app.route('/add_plane', methods=['GET', 'POST'])
def add_plane():
    form = airplaneForm()
    if request.method=="POST":
        airlinename = form.airlinename.data
        print(airlinename)
        planeid= form.planeid.data
        seatnum = form.seats.data
        with staff_connection.cursor(pymysql.cursors.DictCursor) as mycursor:
            query = f"select * from airline where airline_name = '{airlinename}'"
            mycursor.execute(query)
            checker = mycursor.fetchone()
            if checker is None:
                mycursor.close()
                flash('UPDATE FAILED, MUST HAVE VALID AIR LINE NAME', 'danger')
                return redirect(url_for('home'))
            query = f"insert into airplane values('{airlinename}',{planeid},{seatnum})"
            mycursor.execute(query)
            staff_connection.commit()
            mycursor.close()
            flash('NEW PLANE ADDED!', 'success')
            return redirect(url_for('home'))
    return render_template('new_plane.html', form=form)
            



#operater use case
@app.route('/update_flight', methods=['GET', 'POST'])
def update_flight():
    form = Operator_Update_Flight_Form()
    if form.validate_on_submit():
        with staff_connection.cursor(pymysql.cursors.DictCursor) as mycursor:
            str_flight_num = form.flight_num.data
            query = f"Select flight_num from flight where flight_num = '{str_flight_num}'"
            mycursor.execute(query)
            data = mycursor.fetchone()
            if data is None:
                flash('Flight is not found, type in the right flight number', 'danger')
                mycursor.close()
                return redirect(request.url)
            else:
                str_flight_status = str(form.flight_status.data)
                str_flight_num = str(form.flight_num.data)
                query = f"UPDATE flight SET status = '{str_flight_status}' WHERE flight_num = '{str_flight_num}';"
                mycursor.execute(query)
                staff_connection.commit()
                mycursor.close()
                flash('Flight status updated', 'success')
                return redirect(url_for('home'))

    return render_template('staff_update_flight.html', form=form)







