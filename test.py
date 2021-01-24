import mysql.connector

def create_todo_db():
    f = open("various/db.txt", "r")
    db_user = f.readline().rstrip("\n")
    db_pass = f.readline().rstrip("\n")
    db_host = f.readline().rstrip("\n")
    f.close()
    print(db_host, db_pass, db_user)
    mydb = mysql.connector.connect(
        host=db_host,
        user=db_user,
        password=db_pass,
        database="tess"
    )
    mycursor = mydb.cursor()
    mycursor.execute("CREATE DATABASE Rene_todo")
    mydb = mysql.connector.connect(
        host=db_host,
        user=db_user,
        password=db_pass,
        database="Rene_todo"
    )

    mycursor = mydb.cursor()

    mycursor.execute("CREATE TABLE Standardlist (item VARCHAR(255), state VARCHAR(255))")


create_todo_db()