from model import connection, agent_connection, staff_connection, customer_connection
import pymysql
import bcrypt
from datetime import date,datetime
from dateutil.relativedelta import relativedelta
session = {}
data={}
with staff_connection.cursor(pymysql.cursors.DictCursor) as mycursor:
    query = f"Select airplane_id from airplane where airline_name = 'Jet Blue'"
    mycursor.execute(query)
    data = mycursor.fetchall()
    planes = [i['airplane_id'] for i in data]
    print(planes)