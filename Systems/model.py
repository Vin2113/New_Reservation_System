import pymysql
connection = pymysql.connections.Connection(host='localhost',
                             user='root',
                             password='NGERNNGa_382563!@',
                            database = 'project_demo',
                            port = 3307
                           )
my_cursor = connection.cursor()