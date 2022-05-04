from model import my_cursor, connection

query = f"SELECT email, password from customer WHERE email = 'vincent@gmail.com'"

my_cursor.execute(query)
account = my_cursor.fetchone()
print(account)