import mysql.connector
mydb = mysql.connector.connect(
  host="localhost",
  user="Rene",
  password="CX30re92#",
  database="tess"
)

mycursor = mydb.cursor(dictionary=True)

mycursor.execute("SELECT user FROM userdata ")
users = {}
myresult = mycursor.fetchall()

for x in myresult:
  print(x)