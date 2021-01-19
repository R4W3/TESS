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
            password=password,
        )
        if mydb:
            return redirect('/setup2')
        else:
            return redirect('/setup')

    return render_template("setup_1.html")

@app.route("/setup2")
def setup2():

    return render_template("setup_2.html")

if __name__ == "__main__":
    app.run(debug=True)