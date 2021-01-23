from flask import Flask, render_template, redirect, request
import mysql.connector


app = Flask(__name__)


@app.route("/")
def welcome():

    return render_template("setup_welcome.html")


@app.route("/setup", methods=['GET', 'POST'])
def setup_1():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        host = request.form['host']
        mydb = mysql.connector.connect(
            host=host,
            user=username,
            password=password
        )
        if mydb:
            f = open("various/db.txt", "w")
            f.write(username+"\n"+password+"\n"+host)
            f.close()
            mydb = mysql.connector.connect(
                host=host,
                user=username,
                password=password
            )
            mycursor = mydb.cursor()
            mycursor.execute("CREATE DATABASE tess")
            return redirect('/setup2')
        else:
            return redirect('/setup')

    return render_template("setup_1.html")


@app.route("/setup2", methods=['GET', 'POST'])
def setup2():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
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
        mycursor.execute("CREATE TABLE userdata (user VARCHAR(255), pass VARCHAR(255))")
        mydb = mysql.connector.connect(
            host=db_host,
            user=db_user,
            password=db_pass,
            database="tess"
        )
        mycursor = mydb.cursor()
        sql = "INSERT INTO userdata (user, pass) VALUES (%s, %s)"
        val = (username, password)
        mycursor.execute(sql, val)
        mydb.commit()
        print(mycursor.rowcount, "record inserted.")

        mydb = mysql.connector.connect(
            host=db_host,
            user=db_user,
            password=db_pass,
            database="tess"
        )
        mycursor = mydb.cursor()
        sett = "CREATE TABLE ",username," (setting VARCHAR(255), value VARCHAR(255))"
        mycursor.execute(sett)
        mydb = mysql.connector.connect(
            host=db_host,
            user=db_user,
            password=db_pass,
            database="tess"
        )
        mycursor = mydb.cursor()
        sett = "INSERT INTO ",username," (setting, value) VALUES (%s, %s)"
        sql = sett
        val = ("theme", "dark")
        mycursor.execute(sql, val)

        mydb.commit()

        print(mycursor.rowcount, "record inserted.")



        return redirect("/setup3")

    return render_template("setup_2.html")


@app.route("/setup3")
def setup3():

    return render_template("setup_3.html")


if __name__ == "__main__":
    app.run(debug=True)
