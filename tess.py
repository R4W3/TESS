from __future__ import print_function
from flask import Flask, render_template, redirect, request, session
import mysql.connector
from lang import en
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

l = en
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

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
    ua = str(request.user_agent)
    print(ua)
    if "iPhone" and "OS 14" in ua:
        h1_size = "calc(1.375rem + 3vw)"
    else:
        h1_size = "calc(1.375rem + 1.5vw)"
    darkmode = "1"
    if darkmode == "1":
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

    return render_template("page_index.html", l=l, username=username, bg_color=bg_color, element_color=element_color, text_color=text_color, accent_color=accent_color, accent2_color=accent2_color, text_alt_color=text_alt_color, h1_size=h1_size)


@app.route("/settings")
def settings():
    if "user" in session:
        pass
    else:
        return redirect("/login", code=302)
    username = session["user"]
    ua = str(request.user_agent)
    print(ua)
    if "iPhone" and "OS 14" in ua:
        h1_size = "calc(1.375rem + 3vw)"
    else:
        h1_size = "calc(1.375rem + 1.5vw)"
    darkmode = "1"
    if darkmode == "1":
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

    return render_template("page_settings.html", l=l, username=username, bg_color=bg_color, element_color=element_color, text_color=text_color, accent_color=accent_color, accent2_color=accent2_color, text_alt_color=text_alt_color, h1_size=h1_size)



@app.route("/app_todo", methods=['GET', 'POST'])
def app_todo():
    if "user" in session:
        pass
    else:
        return redirect("/login", code=302)
    username = session["user"]

    return render_template("app_todo.html", l=l, username=username)


@app.route("/app_weather")
def app_weather():
    if "user" in session:
        pass
    else:
        return redirect("/login", code=302)
    username = session["user"]

    return render_template("app_weather.html", l=l, username=username)


@app.route("/app_calendar")
def calendar():
    if "user" in session:
        pass
    else:
        return redirect("/login", code=302)
    username = session["user"]
    creds = None

    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)

    now = datetime.datetime.utcnow().isoformat() + 'Z'
    print('Getting the upcoming 10 events')
    events_result = service.events().list(calendarId='primary', timeMin=now,
                                          maxResults=10, singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])
    print(events)
    if not events:
        print('No upcoming events found.')
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(start, event['summary'])


    return render_template("app_calendar.html", l=l, username=username, events=events, start=start)


if __name__ == "__main__":
    app.run(host='localhost',debug=True)
