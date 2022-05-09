from model import connection, agent_connection, staff_connection, customer_connection
import pymysql
import bcrypt
from datetime import date,datetime
from dateutil.relativedelta import relativedelta
session = {}
data={}
with staff_connection.cursor(pymysql.cursors.DictCursor) as mycursor:
    query = f"Select email, sum(price * .1) as commissions from (select email, booking_agent_id from booking_agent natural join booking_agent_work_for where airline_name = 'Jet Blue') as T join purchases on T.booking_agent_id = purchases.booking_agent_id natural join ticket natural join flight  Where purchase_date > Date_Sub(curdate(), INTERVAL 30 DAY) group by email order by commissions DESC Limit 5"
    mycursor.execute(query)
    data = mycursor.fetchall()
    session['data'] = data
    email = []
    commissions = []
    for i in data:
        email.append(i['email'])
        commissions.append(float(i['commissions']))
    print(email)
    print(commissions)