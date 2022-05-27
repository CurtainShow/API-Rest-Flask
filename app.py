import json, os, pickle, jwt, flask
from flask import Flask, jsonify, request, make_response
import pandas as pd
from datetime import datetime, timedelta
from functools import wraps
import logging

logging.basicConfig(filename='logs.log', level=logging.INFO, format='%(asctime)s %(name)s %(message)s')

app = Flask(__name__)

def group_by(list_input) :
    with open(list_input[0], encoding='utf-8') as data:
        df = pd.read_json(data).T
    df['count'] = df.groupby(list_input[1])[list_input[1]].transform('count')

    grouped_data = df[[list_input[1], 'count']].groupby(by=list_input[1]).count().sort_values(by='count', ascending=False)
    json_grouped_data = grouped_data.to_json()
    return json_grouped_data

def token_required(func):
    """
    @describe:
        function verifying if the Cookie with the JWT Token is present and valid
    @param:
        -A function
    @return:
        -A message if the cookie is not present and an error code
        -A message if the cookie's data is not valid and an error code
        -A decorator
    """
    @wraps(func)
    def decorated(*args, **kwargs):
        token=None
        if request.cookies.get('access-token'):
            token = request.cookies.get('access-token')
            try:
                data = jwt.decode(token, 'abcdefg', algorithms=['HS256'])
                app.logger.info('Token verified')
            except:
                app.logger.info('Token not valid')
                return jsonify({'Alert!': 'Token invalid'}), 403

        if token==None:
            app.logger.info('Token missing')
            return jsonify({'Alert!': 'Token is missing!'}), 401

        return func(*args, **kwargs)
    return decorated

def not_null(list_input):
    with open(list_input[0], encoding='utf-8') as data:
        df = pd.read_json(data).T
    data_without_non_null = df.dropna(subset=list_input[1])
    json_not_null_data = data_without_non_null.to_json()
    return json_not_null_data


@app.route("/")
def hello_world():
    app.logger.info('Open API')
    return "<p>Hello, world !</p>"

@app.route("/health")
def health():
    """
         @describe:
            function to verify if the API is alive
        @param:
            -No parameters
        @return:
            -A message and success code
    """
    app.logger.info('Get Health status')
    return "API is healthy :3",200

@app.route("/compute/grouped", methods=["GET", "POST"])
@token_required
def get_or_post_group_by():
    if request.method == "GET":
        list_input = []
        for a in request.get_json():
            list_input.append(request.get_json()[a])
            print(f"{a} : {request.get_json()[a]}")
            app.logger.info('Get a group by')
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
            app.logger.info('Post a group by')
        return new_file

@app.route("/compute/not_null", methods=["GET", "POST"])
@token_required
def not_null_data():
    if request.method == "GET":
        list_input = []
        for a in request.get_json():
            list_input.append(request.get_json()[a])
            print(f"{a} : {request.get_json()[a]}")
        app.logger.info('Get a not null info')
        return not_null(list_input)

    elif request.method == "POST":
        list_input = []
        for a in request.get_json():
            list_input.append(request.get_json()[a])
            print(f"{a} : {request.get_json()[a]}")
        output = not_null(list_input)
        new_file = f"{os.getcwd()}/{list_input[2]}"
        with open(new_file, 'w') as json_file:
            json_file.write(output)
        app.logger.info('Post a not null info')
        return new_file

@app.route('/login')
def login():
    """
    @describe:
        function to log a user and get a cookie with a JWT Token generated inside of it
    @param:
        -No parameters
    @return:
        -A cookie with the JWT Token
        -A message if the authentication failed and an error code
     """
    auth = request.authorization

    if auth and auth.password == 'password' and auth.username == 'login':
        payload = {'user': auth.username, 'expiration': str(datetime.utcnow() + timedelta(seconds=60))}
        token = jwt.encode(payload, 'abcdefg')
        response = flask.Response()
        response.set_cookie('access-token', token)
        app.logger.info('Logged in')
        return response
    return make_response('Could not verify!', 401, {'WWW-Authenticate': 'Basic realm="Login required"'})

app.run()
