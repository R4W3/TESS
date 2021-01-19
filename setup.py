from flask import Flask, render_template

app = Flask(__name__)

if __name__ == "__main__": #finally run the fucker
    app.run(debug=True)