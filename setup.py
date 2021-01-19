from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def welcome():

    return render_template("setup_welcome.html")


if __name__ == "__main__": #finally run the fucker
    app.run(debug=True)