import pymysql.cursors
import cryptography
from model import customer_connection

with customer_connection.cursor(pymysql.cursors.DictCursor) as mycursor:
    query = 'Select max(ticket_id) from ticket'
    mycursor.execute(query)
    data = mycursor.fetchall()
    print(data)
    # query = f"INSERT INTO ticket Values('{data[0]['max(ticket_id)'] +1}','Jet Blue', 455)"
    # mycursor.execute(query)
    # customer_connection.commit()
    # mycursor.close()

