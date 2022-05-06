from Reservation import app, bcrypt
from Forms import RegistrationForm, LoginForm, SearchForm
from flask_login import login_user, current_user, logout_user, login_required
from flask import render_template, flash, redirect, session, request, url_for
import datetime
from model import my_cursor, connection
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

@app.route('/search', methods = ["POST"])
def search():
    form=SearchForm()
    if form.validate_on_submit():
        depart = form.depart.data
        dest = form.arrival.data
        date = form.time.data
        if(date != ""):
            dateandtime=date.split(',')
            date = dateandtime[0].strip()
            time = dateandtime[1].strip()
            date = date.split('/')
            time= time.split(':')
            dateandtime = datetime.datetime(int(date[2]),int(date[0]),int(date[1]),int(time[0]),int(time[1]))
            dateandtime = '\'' + str(dateandtime) + '\''
            print(dateandtime)
        else:
            dateandtime = "departure_time"
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
        with connection.cursor(pymysql.cursors.DictCursor) as mycursor:
            mycursor.execute("select * from available_flights where departure_airport =" + departa + " and arrival_airport ="+ desta +" and departure_time = " + dateandtime)
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
        dob_time = form.date_of_birth.data
        #datetime.datetime(int(form.date_of_birth.data[-4:-1]), int(form.date_of_birth.data[0:2]), int(form.date_of_birth.data[3:5]))
        query = f"Insert INTO customer VALUES('{email}', '{form.name.data}', '{hashed_password}','{form.building_number.data}','{form.street.data}','{form.city.data}','{form.state.data}', {phone_number} ,'{form.passport_number.data}','{exp_time}','{form.passport_country.data}','{dob_time}')"
        
        my_cursor.execute(query)
        connection.commit()
        flash(f'You can now login {form.name.data}!', 'success')
        return redirect(url_for('login'))
    return render_template('Register.html', title='Register', form=form)


@app.route('/customer_login', methods=["GET", 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        str_email = str(form.email.data)
        password = form.password.data
        query = f"SELECT email, password from customer WHERE email = '{str_email}'"
        my_cursor.execute(query)
        account = my_cursor.fetchone()
        #checking user data from database for verification
        if account and bcrypt.check_password_hash(account[1],form.password.data):
            session['loggedin'] = True
            session['email'] = account[0]
            session['password'] = account[1]
            flash('Login Successful', 'success')
            return redirect(url_for('home'))
        else:
            flash('Login unsuccesful, please check username and password.', 'danger')
    return render_template('Login.html', title='Login', form=form)

@app.route('/logout', methods=["GET", 'POST'])
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('email', None)
   session.pop('password', None)
   # Redirect to login page
   return redirect(url_for('login'))



