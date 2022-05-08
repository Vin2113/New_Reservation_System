from model import connection, agent_connection, staff_connection
import pymysql
import bcrypt
session = {}
with agent_connection.cursor(pymysql.cursors.DictCursor) as my_cursor:
    query = f"SELECT email, password, booking_agent_id from booking_agent WHERE email = 'vin321@gmail.com'"
    my_cursor.execute(query)
    account = my_cursor.fetchone()
    print(account)

print(session)