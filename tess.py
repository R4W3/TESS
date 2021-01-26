from __future__ import print_function
from flask import Flask, render_template, redirect, request, session, url_for
import mysql.connector
from lang_en import english
from lang_de import german
import requests
import speech_recognition as sr
import pyttsx3

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
    l = english

    return render_template("page_login.html", l=l)


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")


@app.route("/", methods=['GET', 'POST'])
def index():
    if "user" in session:
        pass
    else:
        return redirect("/login", code=302)
    username = session["user"]
    if request.method == 'POST':
        f = request.files['audio_data']
        print(f)
        with open('audio'+username+'.wav', 'wb') as audio:
            f.save(audio)
        print('file uploaded successfully')
        return redirect(url_for('voice'))

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
    mycursor = db.cursor()
    sql = "SELECT * FROM " + username + " WHERE setting ='language'"
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    for x in myresult:
        l = x[1]
    if l == "en":
        l = english
    if l == "de":
        l = german
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
    if "iPhone" in ua:
        h1_size = "calc(1.375rem + 3vw)"
        client = "iPhone"
    else:
        h1_size = "calc(1.375rem + 1.5vw)"
        client = "Desktop"

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

    return render_template("page_index.html", l=l, client=client, username=username, role=role, bg_color=bg_color, element_color=element_color, text_color=text_color, accent_color=accent_color, accent2_color=accent2_color, text_alt_color=text_alt_color, h1_size=h1_size)


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
    db = mysql.connector.connect(
        host=db_host,
        user=db_user,
        password=db_pass,
        database="tess"
    )
    mycursor = db.cursor()
    sql = "SELECT * FROM " + username + " WHERE setting ='language'"
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    for x in myresult:
        l = x[1]
    if l == "en":
        l = english
    if l == "de":
        l = german
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
    try:
        api_key
    except NameError:
        temp = "No connection / Provide an API Key"
        pass
    else:
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
        new_language = req.get("language")
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
        mydb = mysql.connector.connect(
            host=db_host,
            user=db_user,
            password=db_pass,
            database="tess"
        )
        mycursor = mydb.cursor()
        sql = "UPDATE " + username + " SET value = '" +new_language+ "' WHERE setting = 'language'"
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
    db = mysql.connector.connect(
        host=db_host,
        user=db_user,
        password=db_pass,
        database="tess"
    )
    mycursor = db.cursor()
    sql = "SELECT * FROM " + username + " WHERE setting ='language'"
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    for x in myresult:
        l = x[1]
    if l == "en":
        l = english
    if l == "de":
        l = german
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
    if "iPhone" in ua:
        h1_size = "calc(1.375rem + 3vw)"
        client = "iPhone"
    else:
        h1_size = "calc(1.375rem + 1.5vw)"
        client = "Desktop"

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

    return render_template("page_lights.html", username=username, client=client, l=l, bg_color=bg_color, element_color=element_color, text_color=text_color, accent_color=accent_color, accent2_color=accent2_color, text_alt_color=text_alt_color, h1_size=h1_size)


@app.route("/documentation")
def docs():
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
    db = mysql.connector.connect(
        host=db_host,
        user=db_user,
        password=db_pass,
        database="tess"
    )
    mycursor = db.cursor()
    sql = "SELECT * FROM " + username + " WHERE setting ='language'"
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    for x in myresult:
        l = x[1]
    if l == "en":
        l = english
    if l == "de":
        l = german
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
    if "iPhone" in ua:
        h1_size = "calc(1.375rem + 3vw)"
        client = "iPhone"
    else:
        h1_size = "calc(1.375rem + 1.5vw)"
        client = "Desktop"

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

    return render_template("documentation.html", username=username, l=l, bg_color=bg_color, element_color=element_color,
                           text_color=text_color, accent_color=accent_color, accent2_color=accent2_color,
                           text_alt_color=text_alt_color, h1_size=h1_size, client=client)


@app.route("/add_user", methods=['GET', 'POST'])
def new_user():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
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
        mycursor.execute("CREATE TABLE "+username+" (setting VARCHAR(255), value VARCHAR(255))")

        mydb = mysql.connector.connect(
            host=db_host,
            user=db_user,
            password=db_pass,
            database="tess"
        )
        mycursor = mydb.cursor()
        sql = "INSERT INTO "+username+" (setting, value) VALUES (%s, %s)"
        val = [
            ("role", role),
            ("theme", "dark"),
            ("language", "en")
            ]
        mycursor.executemany(sql, val)
        mydb.commit()
        print(mycursor.rowcount, "was inserted.")
        return redirect("/")

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
    db = mysql.connector.connect(
        host=db_host,
        user=db_user,
        password=db_pass,
        database="tess"
    )
    mycursor = db.cursor()
    sql = "SELECT * FROM " + username + " WHERE setting ='language'"
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    for x in myresult:
        l = x[1]
    if l == "en":
        l = english
    if l == "de":
        l = german
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
    if "iPhone" in ua:
        h1_size = "calc(1.375rem + 3vw)"
        client = "iPhone"
    else:
        h1_size = "calc(1.375rem + 1.5vw)"
        client = "Desktop"

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
    return render_template("add_user.html", username=username, l=l, bg_color=bg_color, element_color=element_color,
                           text_color=text_color, accent_color=accent_color, accent2_color=accent2_color,
                           text_alt_color=text_alt_color, h1_size=h1_size, client=client)


@app.route("/todo")
def todo():
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
    db = mysql.connector.connect(
        host=db_host,
        user=db_user,
        password=db_pass,
        database="tess"
    )
    mycursor = db.cursor()
    sql = "SELECT * FROM " + username + " WHERE setting ='language'"
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    for x in myresult:
        l = x[1]
    if l == "en":
        l = english
    if l == "de":
        l = german
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
    if "iPhone" in ua:
        h1_size = "calc(1.375rem + 3vw)"
        client = "iPhone"
    else:
        h1_size = "calc(1.375rem + 1.5vw)"
        client = "Desktop"

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
    db_db = username+"_todo"
    db = mysql.connector.connect(
        host=db_host,
        user=db_user,
        password=db_pass,
        database=db_db
    )
    mycursor = db.cursor()
    mycursor.execute("SHOW TABLES")

    for x in mycursor:
        print(x)
        tables = list(x)
    for item in tables:
        db_db = username + "_todo"
        db = mysql.connector.connect(
            host=db_host,
            user=db_user,
            password=db_pass,
            database=db_db
        )
        mycursor = db.cursor()
        mycursor.execute("SELECT * FROM "+item+"")
        for y in myresult:
            print(y)
            items = list(y)

    return render_template("page_todo.html", username=username, l=l, bg_color=bg_color, element_color=element_color,
                           text_color=text_color, accent_color=accent_color, accent2_color=accent2_color,
                           text_alt_color=text_alt_color, h1_size=h1_size, client=client, tables=tables, items=items)


@app.route("/voice")
def voice():
    if "user" in session:
        pass
    else:
        return redirect("/login", code=302)
    username = session["user"]
    engine = pyttsx3.init()
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
    mycursor = db.cursor()
    sql = "SELECT * FROM " + username + " WHERE setting ='language'"
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    voices = engine.getProperty('voices')
    for x in myresult:
        l = x[1]
    if l == "en":
        l = english
        voiceout = voices[1].id
    if l == "de":
        l = german
        voiceout = voices[0].id
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
    if "iPhone" in ua:
        h1_size = "calc(1.375rem + 3vw)"
        client = "iPhone"
    else:
        h1_size = "calc(1.375rem + 1.5vw)"
        client = "Desktop"

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
    r = sr.Recognizer()
    audiotranscribe = "audio"+username+".wav"
    with sr.AudioFile(audiotranscribe) as source:
        audio = r.record(source)
    try:
        recognized = r.recognize_google(audio)
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
        recognized = "fail"
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))
        recognized = "noconnection"

    if "test" in recognized:
        text = l[44]
        engine.setProperty('rate', 150)
        engine.setProperty('voice', voiceout)
        engine.save_to_file(text, 'static/result'+username+'.mp3')
        engine.runAndWait()
        result = "test"
    elif "weather" and "today" in recognized:
        text = l[45]
        engine.setProperty('rate', 150)
        engine.setProperty('voice', voiceout)
        engine.save_to_file(text, 'static/result' + username + '.mp3')
        engine.runAndWait()
        result = "weather_today"

    resultaudio = '/static/result'+username+'.mp3'


    return render_template("page_voice.html", username=username, l=l, bg_color=bg_color, element_color=element_color,
                           text_color=text_color, accent_color=accent_color, accent2_color=accent2_color,
                           text_alt_color=text_alt_color, h1_size=h1_size, client=client, recognized=recognized,
                           result=result, resultaudio=resultaudio)


if __name__ == "__main__":
    app.run(host='localhost', debug=True)
