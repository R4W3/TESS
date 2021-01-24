import mysql.connector

f = open("db.txt", "r")
db_user = f.readline().rstrip("\n")
db_pass = f.readline().rstrip("\n")
db_host = f.readline().rstrip("\n")
f.close()
mydb = mysql.connector.connect(
  host=db_host,
  user=db_user,
  password=db_pass
)

mycursor = mydb.cursor()

mycursor.execute("SHOW DATABASES")

for x in mycursor:
  print(x)