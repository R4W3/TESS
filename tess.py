from __future__ import print_function
from flask import Flask, render_template, redirect, request, session, url_for
from flask_compress import Compress
import mysql.connector
from lang_en import english
from lang_de import german
import requests
import speech_recognition as sr
import pyttsx3
import feedparser
import re

app = Flask(__name__)
app.secret_key = "1gfh456fdg764poj5423ß0#+453"
Compress(app)


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
            session["user"] = username
            session["language"] = l
            return redirect("/", code=302)
        else:
            return redirect("/login")
    l = english

    return render_template("page_login.html", l=l)


@app.route("/logout")
def logout():
    session.pop("user", None)
    session.pop("language", None)
    return redirect("/login")


@app.route("/", methods=['GET', 'POST'])
def index():
    if "user" in session:
        pass
    else:
        return redirect("/login", code=302)
    username = session["user"]
    l = session["language"]
    if l == "en":
        l = english
    if l == "de":
        l = german
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

    mydb = mysql.connector.connect(
        host=db_host,
        user=db_user,
        password=db_pass,
        database="tess"
    )
    mycursor = mydb.cursor(dictionary=True)
    mycursor.execute("SELECT user FROM userdata ")
    users = {}
    userlist = mycursor.fetchall()

    return render_template("page_index.html", l=l, client=client, username=username, role=role, bg_color=bg_color,
                           element_color=element_color, text_color=text_color, accent_color=accent_color,
                           accent2_color=accent2_color, text_alt_color=text_alt_color, h1_size=h1_size, userlist=userlist)


@app.route("/weather_call")
def weather():
    if "user" in session:
        pass
    else:
        return redirect("/login", code=302)
    username = session["user"]
    l = session["language"]
    if l == "en":
        l = english
    if l == "de":
        l = german
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
        session["language"] = new_language
        return redirect("/")


@app.route("/lights")
def lights():
    if "user" in session:
        pass
    else:
        return redirect("/login", code=302)
    username = session["user"]
    l = session["language"]
    if l == "en":
        l = english
    if l == "de":
        l = german
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
    l = session["language"]
    if l == "en":
        l = english
    if l == "de":
        l = german
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
    l = session["language"]
    if l == "en":
        l = english
    if l == "de":
        l = german
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


@app.route("/voice")
def voice():
    if "user" in session:
        pass
    else:
        return redirect("/login", code=302)
    username = session["user"]
    l = session["language"]
    if l == "en":
        l = english
    if l == "de":
        l = german
    engine = pyttsx3.init()
    f = open("various/db.txt", "r")
    db_user = f.readline().rstrip("\n")
    db_pass = f.readline().rstrip("\n")
    db_host = f.readline().rstrip("\n")
    f.close()
    if l == english:
        voiceout = voices[1].id
    if l == german:
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
            engine.save_to_file(text, 'static/result' + username + '.mp3')
            engine.runAndWait()
            result = "test"
        elif "weather" and "today" in recognized:
            text = l[45]
            engine.setProperty('rate', 150)
            engine.setProperty('voice', voiceout)
            engine.save_to_file(text, 'static/result' + username + '.mp3')
            engine.runAndWait()
            result = "weather_today"
        elif "open" and "settings" in recognized:
            text = l[48]
            engine.setProperty('rate', 150)
            engine.setProperty('voice', voiceout)
            engine.save_to_file(text, 'static/result' + username + '.mp3')
            engine.runAndWait()
            result = "settings"
    elif l == "de":
        l = german
        with sr.AudioFile(audiotranscribe) as source:
            audio = r.record(source)
        try:
            recognized = r.recognize_google(audio, language="de-DE")
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
            engine.save_to_file(text, 'static/result' + username + '.mp3')
            engine.runAndWait()
            result = "test"
        elif "wetter" and "heute" in recognized:
            text = l[45]
            engine.setProperty('rate', 150)
            engine.setProperty('voice', voiceout)
            engine.save_to_file(text, 'static/result' + username + '.mp3')
            engine.runAndWait()
            result = "weather_today"
        elif "öffne" and "einstellungen" in recognized:
            text = l[48]
            engine.setProperty('rate', 150)
            engine.setProperty('voice', voiceout)
            engine.save_to_file(text, 'static/result' + username + '.mp3')
            engine.runAndWait()
            result = "settings"

    resultaudio = '/static/result'+username+'.mp3'

    return render_template("page_voice.html", username=username, l=l, bg_color=bg_color, element_color=element_color,
                           text_color=text_color, accent_color=accent_color, accent2_color=accent2_color,
                           text_alt_color=text_alt_color, h1_size=h1_size, client=client, recognized=recognized,
                           result=result, resultaudio=resultaudio)


@app.route("/news")
def news():
    if "user" in session:
        pass
    else:
        return redirect("/login", code=302)
    username = session["user"]
    l = session["language"]
    if l == "en":
        l = english
    if l == "de":
        l = german
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

    return render_template("/apps/news/news.html", l=l, client=client, username=username, bg_color=bg_color,
                           element_color=element_color, text_color=text_color, accent_color=accent_color,
                           accent2_color=accent2_color, text_alt_color=text_alt_color, h1_size=h1_size)


@app.route("/news/bild")
def news_bild():
    if "user" in session:
        pass
    else:
        return redirect("/login", code=302)
    username = session["user"]
    l = session["language"]
    if l == "en":
        l = english
    if l == "de":
        l = german
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
    d = feedparser.parse('https://www.bild.de/rssfeeds/rss3-20745882,feed=alles.bild.html')
    counter = 0
    newsdict = {

    }
    while counter <= 10:
        newsdict[counter] = {}
        newsdict[counter]["title"] = d.entries[counter].title
        newsdict[counter]["link"] = d.entries[counter].link
        dtemp = d.entries[counter].description
        dtemp3 = re.sub('<[^<]+?>', '', dtemp)
        newsdict[counter]["description"] = dtemp3
        counter += 1

    return render_template("/apps/news/de/bild.html", l=l, client=client, username=username, bg_color=bg_color,
                           element_color=element_color, text_color=text_color, accent_color=accent_color,
                           accent2_color=accent2_color, text_alt_color=text_alt_color, h1_size=h1_size,
                           newsdict=newsdict)


@app.route("/news/bild/politik")
def news_politik_bild():
    if "user" in session:
        pass
    else:
        return redirect("/login", code=302)
    username = session["user"]
    l = session["language"]
    if l == "en":
        l = english
    if l == "de":
        l = german
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
    d = feedparser.parse('https://www.bild.de/rss-feeds/rss-16725492,feed=politik.bild.html')
    counter = 0
    newsdict = {

    }
    while counter <= 10:
        newsdict[counter] = {}
        newsdict[counter]["title"] = d.entries[counter].title
        newsdict[counter]["link"] = d.entries[counter].link
        dtemp = d.entries[counter].description
        dtemp3 = re.sub('<[^<]+?>', '', dtemp)
        newsdict[counter]["description"] = dtemp3
        counter += 1

    return render_template("/apps/news/de/bild_politik.html", l=l, client=client, username=username, bg_color=bg_color,
                           element_color=element_color, text_color=text_color, accent_color=accent_color,
                           accent2_color=accent2_color, text_alt_color=text_alt_color, h1_size=h1_size,
                           newsdict=newsdict)


@app.route("/news/bild/sport")
def news_sport_bild():
    if "user" in session:
        pass
    else:
        return redirect("/login", code=302)
    username = session["user"]
    l = session["language"]
    if l == "en":
        l = english
    if l == "de":
        l = german
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
    d = feedparser.parse('https://www.bild.de/rss-feeds/rss-16725492,feed=sport.bild.html')
    counter = 0
    newsdict = {

    }
    readOutLoud = ""
    while counter <= 10:
        newsdict[counter] = {}
        newsdict[counter]["title"] = d.entries[counter].title
        newsdict[counter]["link"] = d.entries[counter].link
        dtemp = d.entries[counter].description
        dtemp3 = re.sub('<[^<]+?>', '', dtemp)
        newsdict[counter]["description"] = dtemp3
        readOutLoud += d.entries[counter].title+"\n"
        counter += 1
    print(readOutLoud)
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    voiceout = voices[0].id
    engine.setProperty('rate', 150)
    engine.setProperty('voice', voiceout)
    engine.save_to_file(readOutLoud, 'static/mp3/news/bild_sport.mp3')
    engine.runAndWait()
    newsaudio = 'mp3/news/bild_sport'+username+'.mp3'

    return render_template("/apps/news/de/bild_sport.html", l=l, client=client, username=username, bg_color=bg_color,
                           element_color=element_color, text_color=text_color, accent_color=accent_color,
                           accent2_color=accent2_color, text_alt_color=text_alt_color, h1_size=h1_size,
                           newsdict=newsdict, newsaudio=newsaudio)



if __name__ == "__main__":
    app.run(host='localhost', debug=True)
