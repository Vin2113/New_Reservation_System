import mysql.connector
connection = mysql.connector.connect(host='localhost',
                             user='root',
                             password='Vl1021996499.',
                            database = 'reservation_system'
                           )
my_cursor = connection.cursor()
# my_cursor.execute(("SHOW TABLES"))
# for table in my_cursor:
#     print(table[0])
#my_cursor.execute("SELECT email,password FROM customer")
stuff = "INSERT INTO airline VALUES('China Eastern')"
my_cursor.execute(stuff)
#
connection.commit()
# my_cursor.fetchall()