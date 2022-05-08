import pymysql
connection = pymysql.connect(host='localhost',
                             user ='root',
                             password='Hotpot123',
                             database='project_demo',
                             port = 3307
                             )
customer_connection = pymysql.connect(host = 'localhost',
                             user = 'Customer',
                          password='123',
                          database='project_demo'
                          ,port = 3307
                            )
agent_connection = pymysql.connect(host = 'localhost',
                             user = 'Agent',
                             password= '123',
                            database ='project_demo',
                             port = 3307
                                   )
staff_connection = pymysql.connect(host = 'localhost',
                             user = 'Staff',
                             password= '123',
                            database = 'project_demo',
                             port = 3307
                                   )
