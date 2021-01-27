import mysql.connector
mydb = mysql.connector.connect(
  host="localhost",
  user="Rene",
  password="CX30re92#",
  database="tess"
)

mycursor = mydb.cursor()

mycursor.execute("SELECT user FROM userdata ")

myresult = mycursor.fetchall()

for x in myresult:
    final = list(x)

    print(final)


