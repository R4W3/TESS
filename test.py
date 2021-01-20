import mysql.connector


mydb = mysql.connector.connect(
    host="127.0.0.1",
    user="Rene",
    password="CX30re92#",
    database="tess"
)
mycursor = mydb.cursor()
mycursor.execute("SHOW Tables")
for (table_name,) in mycursor:
    if "todo" in table_name:
        print(table_name)