from flask import Flask, render_template, redirect, request, session
import mysql.connector
from lang import en

l = en

app = Flask(__name__)
app.secret_key = "1gfh456fdg764poj5423ß0#+453"


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

    return render_template("page_index.html", l=l, username=username)


@app.route("/app_todo", methods=['GET', 'POST'])
def app_todo():
    if "user" in session:
        pass
    else:
        return redirect("/login", code=302)
    username = session["user"]

    return render_template("app_todo.html", l=l, username=username)


if __name__ == "__main__":
    app.run(debug=True)
