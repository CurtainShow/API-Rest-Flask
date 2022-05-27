import flask
from flask import Flask, jsonify, request, make_response
import jwt
import json,os
import pandas as pd
from datetime import datetime, timedelta
from functools import wraps

app = Flask(__name__)


def group_by(list_input) :
    with open(list_input[0], encoding='utf-8') as data:
        df = pd.read_json(data).T
    print(df.head())
    df['count'] = df.groupby(list_input[1])[list_input[1]].transform('count')

    grouped_data = df[[list_input[1], 'count']].groupby(by=list_input[1]).count().sort_values(by='count', ascending=False)
    json_grouped_data = grouped_data.to_json()
    return json_grouped_data

def token_required(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        token=None
        if request.cookies.get('access-token'):
            token = request.cookies.get('access-token')
            try:
                data = jwt.decode(token, 'abcdefg', algorithms=['HS256'])
            except:
                return jsonify({'Alert!': 'Token invalid'}), 403
        if token==None:
            return jsonify({'Alert!': 'Token is missing!'}), 401

        return func(*args, **kwargs)
    return decorated

@app.route("/")
def hello_world():
    return "<p>Hello, world !</p>"

@app.route("/course", methods=["GET", "POST"])
@token_required
def course_esgi():
    with open('data.json', encoding='utf-8') as json_data:
        data_dict = json.load(json_data)
    return data_dict

@app.route("/course/grouped", methods=["GET", "POST"])
@token_required
def get_or_post_group_by():
    if request.method == "GET":
        list_input = []
        for a in request.get_json():
            list_input.append(request.get_json()[a])
            print(f"{a} : {request.get_json()[a]}")
        return group_by(list_input)

    elif request.method == "POST":
        list_input = []
        for a in request.get_json():
            list_input.append(request.get_json()[a])
            print(f"{a} : {request.get_json()[a]}")
        output = group_by(list_input)
        new_file = f"{os.getcwd()}/{list_input[2]}"
        with open(new_file, 'w') as json_file:
            json_file.write(output)
        return new_file

@app.route('/login')
def login():
    auth = request.authorization

    if auth and auth.password == 'password' and auth.username == 'login':
        payload = {'user': auth.username, 'expiration': str(datetime.utcnow() + timedelta(seconds=60))}
        token = jwt.encode(payload, 'abcdefg')
        response = flask.Response()
        response.set_cookie('access-token', token)
        return response
    return make_response('Could not verify!', 401, {'WWW-Authenticate': 'Basic realm="Login required"'})

app.run()
