import pymysql
from model import staff
connection = pymysql.connect(host='localhost',
                             user='root',
                             password='Vl1021996499.',
                            database = 'reservation_system'
                           )
with staff_connection.cursor(pymysql.cursors.DictCursor) as mycursor:
    query = f"Select email, count(ticket_id) as sales from (select email, booking_agent_id from booking_agent natural join booking_agent_work_for where airline_name = '{session['airline_name']}') as T join purchases on T.booking_agent_id = purchases.booking_agent_id natural join ticket natural join flight  Where purchase_date > Date_Sub(curdate(), INTERVAL 30 DAY) group by email order by sales DESC Limit 5"
    mycursor.execute(query)
    data = mycursor.fetchall()