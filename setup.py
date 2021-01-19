from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def welcome():

    return render_template("setup_welcome.html")

@app.route("/setup")
def setup_1():

    return render_template("setup_1.html")

if __name__ == "__main__": #finally run the fucker
    app.run(debug=True)