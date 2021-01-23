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
    #mycursor.execute("CREATE TABLE Rene (setting VARCHAR(255), value VARCHAR(255))")
    sql = "INSERT INTO rene (setting, value) VALUES (%s, %s)"
    val = ("owm-api", "ef8fbd4d3f92d385771412145a1b36dc")
    mycursor.execute(sql, val)

    mydb.commit()

    print(mycursor.rowcount, "record inserted.")


create_todo_db()