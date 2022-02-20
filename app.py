from flask import Flask
app = Flask('cloud')

@app.route("/")
def home():
    return "HELLO WORLD"