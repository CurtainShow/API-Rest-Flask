from flask import Flask
import json

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, world !</p>"

@app.route("/esgi", methods=["GET", "POST"])
def hello_esgi():
    return "<p>Hello, ESGI !</p>"

@app.route("/course", methods=["GET", "POST"])
def course_esgi():
    with open('data.json', encoding='utf-8') as json_data:
        data_dict = json.load(json_data)
    return data_dict