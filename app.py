from flask import Flask
import json

app = Flask(__name__)

app.config['SECRET_KEY'] = 'abcdefg'

def token_required(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        token=None
        if 'access-token' in request.headers:
            token = request.headers['access-token']
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

@app.route("/esgi", methods=["GET", "POST"])
def hello_esgi():
    return "<p>Hello, ESGI !</p>"

@app.route("/course", methods=["GET", "POST"])
def course_esgi():
    with open('data.json', encoding='utf-8') as json_data:
        data_dict = json.load(json_data)
    return data_dict

@app.route('/protected')
@token_required
def protected():
    return jsonify({'message': 'Only people with a valid token can see this'}), 202


@app.route('/login')
def login():
    auth = request.authorization

    if auth and auth.password == 'password' and auth.username == 'login':
        payload = {'user': auth.username, 'expiration': str(datetime.utcnow() + timedelta(seconds=60))}
        token = jwt.encode(payload, 'abcdefg')

        return jsonify({'token': token ,'decode': jwt.decode(token, 'abcdefg', algorithms=['HS256'])})

    return make_response('Could not verify!', 401, {'WWW-Authenticate': 'Basic realm="Login required"'})
