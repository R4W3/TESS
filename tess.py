from __future__ import print_function
from flask import Flask, render_template, redirect, request, session
import mysql.connector
from lang import en
import requests

l = en

app = Flask(__name__)
app.secret_key = "1gfh456fdg764poj5423ß0#+453"


@app.route('/service-worker.js')
def sw():
    return app.send_static_file('service-worker.js')


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        f = open("various/db.txt", "r")
        db_user = f.readline().rstrip("\n")
        db_pass = f.readline().rstrip("\n")
        db_host = f.readline().rstrip("\n")
        f.close()
        db = mysql.connector.connect(
            host=db_host,
            user=db_user,
            password=db_pass,
            database="tess"
        )
        cursor = db.cursor()
        cursor.execute('SELECT * FROM userdata WHERE user = %s AND pass = %s', (username, password,))
        # Fetch one record and return result
        account = cursor.fetchone()

        if account:
            session["user"] = username
            return redirect("/", code=302)
        else:
            return redirect("/login")

    return render_template("page_login.html", l=l)


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")


@app.route("/")
def index():
    if "user" in session:
        pass
    else:
        return redirect("/login", code=302)
    username = session["user"]
    f = open("various/db.txt", "r")
    db_user = f.readline().rstrip("\n")
    db_pass = f.readline().rstrip("\n")
    db_host = f.readline().rstrip("\n")
    f.close()
    mydb = mysql.connector.connect(
        host=db_host,
        user=db_user,
        password=db_pass,
        database="tess"
    )
    mycursor = mydb.cursor()
    sql = "SELECT * FROM " + username + " WHERE setting ='theme'"
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    for x in myresult:
        theme = x[1]
    mydb = mysql.connector.connect(
        host=db_host,
        user=db_user,
        password=db_pass,
        database="tess"
    )
    mycursor = mydb.cursor()
    sql = "SELECT * FROM " + username + " WHERE setting ='role'"
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    for x in myresult:
        role = x[1]

    ua = str(request.user_agent)
    print(ua)
    if "iPhone" and "OS 14" in ua:
        h1_size = "calc(1.375rem + 3vw)"
        nav = "nav_mobile.html"
    else:
        h1_size = "calc(1.375rem + 1.5vw)"
        nav = "nav_desktop.html"

    if theme == "dark":
        bg_color = "#020202"
        element_color = "#4F4B58"
        text_color = "#C5CBD3"
        text_alt_color = "#C5CBD3"
        accent_color = "#036016"
        accent2_color = '#16db65'

    else:
        bg_color = "#C5CBD3"
        element_color = "#4F4B58"
        text_color = "#fff"
        text_alt_color = "#020202"
        accent_color = "#036016"
        accent2_color = '#16db65'

    return render_template("page_index.html", l=l, username=username, role=role, bg_color=bg_color, element_color=element_color, text_color=text_color, accent_color=accent_color, accent2_color=accent2_color, text_alt_color=text_alt_color, h1_size=h1_size, nav=nav)


@app.route("/weather_call")
def weather():
    if "user" in session:
        pass
    else:
        return redirect("/login", code=302)
    username = session["user"]
    f = open("various/db.txt", "r")
    db_user = f.readline().rstrip("\n")
    db_pass = f.readline().rstrip("\n")
    db_host = f.readline().rstrip("\n")
    f.close()
    mydb = mysql.connector.connect(
        host=db_host,
        user=db_user,
        password=db_pass,
        database="tess"
    )
    mycursor = mydb.cursor()
    sql = "SELECT * FROM "+username+" WHERE setting ='owm-api'"
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    for x in myresult:
        api_key = x[1]
    city_name = "Zeven"
    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    complete_url = base_url + "appid=" + api_key + "&q=" + city_name
    response = requests.get(complete_url)
    x = response.json()
    if x["cod"] != "404":
        y = x["main"]
        current_temperature = y["temp"]
        z = x["weather"]
        weather_description = z[0]["description"]
        tempc = int(current_temperature) - 273.15
        temp = round(tempc)
    else:
        temp = "n"

    return render_template("weather.php", l=l, temp=temp)


@app.route("/settings", methods=['POST'])
def settings():
    if "user" in session:
        pass
    else:
        return redirect("/login", code=302)
    username = session["user"]
    if request.method == 'POST':
        req = request.form
        print(req)
        new_theme = req.get("theme")
        f = open("various/db.txt", "r")
        db_user = f.readline().rstrip("\n")
        db_pass = f.readline().rstrip("\n")
        db_host = f.readline().rstrip("\n")
        f.close()
        mydb = mysql.connector.connect(
            host=db_host,
            user=db_user,
            password=db_pass,
            database="tess"
        )
        mycursor = mydb.cursor()
        sql = "UPDATE "+username+" SET value = '"+new_theme+"' WHERE setting = 'theme'"
        mycursor.execute(sql)
        mydb.commit()
        print(mycursor.rowcount, "record(s) affected")
        return redirect("/")


@app.route("/lights")
def lights():
    if "user" in session:
        pass
    else:
        return redirect("/login", code=302)
    username = session["user"]
    f = open("various/db.txt", "r")
    db_user = f.readline().rstrip("\n")
    db_pass = f.readline().rstrip("\n")
    db_host = f.readline().rstrip("\n")
    f.close()
    mydb = mysql.connector.connect(
        host=db_host,
        user=db_user,
        password=db_pass,
        database="tess"
    )
    mycursor = mydb.cursor()
    sql = "SELECT * FROM " + username + " WHERE setting ='theme'"
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    for x in myresult:
        theme = x[1]
    ua = str(request.user_agent)
    print(ua)
    if "iPhone" and "OS 14" in ua:
        h1_size = "calc(1.375rem + 3vw)"
        nav = "nav_mobile.html"
    else:
        h1_size = "calc(1.375rem + 1.5vw)"
        nav = "nav_desktop.html"

    if theme == "dark":
        bg_color = "#020202"
        element_color = "#4F4B58"
        text_color = "#C5CBD3"
        text_alt_color = "#C5CBD3"
        accent_color = "#036016"
        accent2_color = '#16db65'

    else:
        bg_color = "#C5CBD3"
        element_color = "#4F4B58"
        text_color = "#fff"
        text_alt_color = "#020202"
        accent_color = "#036016"
        accent2_color = '#16db65'

    return render_template("page_lights.html", username=username, l=l, bg_color=bg_color, element_color=element_color, text_color=text_color, accent_color=accent_color, accent2_color=accent2_color, text_alt_color=text_alt_color, h1_size=h1_size, nav=nav)


if __name__ == "__main__":
    app.run(host='localhost', debug=True)
