from model import connection, agent_connection, staff_connection
import pymysql
import bcrypt
session = {}
with staff_connection.cursor() as mycursor:
    query = f"SELECT permission_type From permission WHERE username = 'Vincent123'"
    mycursor.execute(query)
    account = mycursor.fetchall()
    print(account)
    for i in account:
        print(i[0])
    if account[0] == 'Vincent123':
        session['type'] = 'staff'
        session['loggedin'] = True
        session['username'] = account[0][0]
        session['password'] = account[0][0]
        session['airline'] = "Jet Blue"
print(session)