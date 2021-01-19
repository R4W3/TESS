import mysql.connector


mydb = mysql.connector.connect(
    host="127.0.0.1",
    user="Rene",
    password="CX30re92#",
    database="tess"
)
mycursor = mydb.cursor()
mycursor.execute("CREATE TABLE userdata (user VARCHAR(255), pass VARCHAR(255))")