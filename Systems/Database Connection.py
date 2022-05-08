from model import connection, agent_connection, staff_connection
import pymysql

with staff_connection.cursor(pymysql.cursors.DictCursor) as mycursor:
    str_username = '123'
    query = f"Select username from airline_staff where username = '{str_username}' and airline_name = 'Jet Blue'"
    mycursor.execute(query)
    data = mycursor.fetchone()
    print(data)