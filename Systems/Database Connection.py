from model import connection, agent_connection, staff_connection
import pymysql

with staff_connection.cursor(pymysql.cursors.DictCursor) as mycursor:
    query = f"Select email from booking_agent where email = '112'"
    mycursor.execute(query)
    data = mycursor.fetchone()
    print(data)