import pymysql
connection = pymysql.connect(host='localhost',
                             user='root',
                             password='Vl1021996499.',
                            database = 'reservation_system'
                           )
with connection.cursor(pymysql.cursors.DictCursor) as mycursor:
    query = "select * from flight where status = 'Upcoming'"
    mycursor.execute(query)
    data = mycursor.fetchall()
    print(data)