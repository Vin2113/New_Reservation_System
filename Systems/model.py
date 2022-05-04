import pymysql

connection = pymysql.connect(host='localhost',
                             user ='root',
                             password='Vl1021996499.',
                            database = 'reservation_system'
                             )
customer_connection = pymysql.connect(host = 'localhost',
                             user = 'Customer',
                             password= 'Vl3002817',
                            database = 'reservation_system')
agent_connection = pymysql.connect(host = 'localhost',
                             user = 'Agent',
                             password= '123',
                            database = 'reservation_system')
staff_connection = pymysql.connect(host = 'localhost',
                             user = 'Staff',
                             password= '123',
                            database = 'reservation_system')
