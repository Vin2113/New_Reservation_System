from model import connection, agent_connection, staff_connection, customer_connection
import pymysql
import bcrypt
from datetime import date,datetime
from dateutil.relativedelta import relativedelta
session = {}
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
#session['span']