from __future__ import print_function
import os
from datetime import datetime
from flask import Flask, request, Response, flash, url_for, redirect, \
     render_template, abort, send_from_directory
from flask.ext.login import LoginManager, UserMixin, login_required, login_user
from pymongo import MongoClient
import hashlib

app = Flask(__name__)
app.config.from_pyfile('flaskapp.cfg')

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


# mongodb config. Allows for easy testing with local mongodb
connection_string = 'mongodb://localhost:27017'
if 'OPENSHIFT_MONGODB_DB_PASSWORD' in os.environ:
    connection_string = "mongodb://" + os.environ['OPENSHIFT_MONGODB_DB_USERNAME'] + ":" +
    os.environ['OPENSHIFT_MONGODB_DB_PASSWORD'] + "@" +
    os.environ['OPENSHIFT_MONGODB_DB_HOST'] + ':' +
    os.environ['OPENSHIFT_MONGODB_DB_PORT']' + '/' +
    os.environ['OPENSHIFT_APP_NAME'];


class User(UserMixin):
    def __init__(self, username, password):
        self.id = username
        self.password = password

    @classmethod
    def from_entry(cls, entry):
        if entry is None:
            return None
        return User(entry['username'], entry['password'])

    @classmethod
    def get(cls, id, password=None):
        client = MongoClient(connection_string)
        users = client['timeflex']['users']
        if password:
            password_hash = hashlib.md5(password).hexdigest()
            user_entry = users.find_one({'username': id, 'password': password_hash})
        else:
            user_entry = users.find_one({'username': id})
        return User.from_entry(user_entry)

    @classmethod
    def register(cls, id, name, email, password):
        password_hash = hashlib.md5(password).hexdigest()
        client = MongoClient(connection_string)
        users = client['timeflex']['users']
        users.insert_one({
            'username': id,
            'name': name,
            'email': email,
            'password': password_hash})


@app.route('/register' , methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    User.register(request.form['username'], request.form['name'], request.form['email'], request.form['password'])
    flash('User successfully registered')
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.get(request.form['username'], request.form['password'])
        if user:
            login_user(user)
            flash("Logged in successfully!", category='success')
            return redirect(request.args.get("next") or url_for("index"))
        flash("Wrong username or password!", category='error')
    return render_template('login.html')


@login_manager.user_loader
def load_user(username):
    return User.get(username)


@app.route("/", methods=["GET"])
def index():
    return render_template('index.html')


@app.route("/protected/", methods=["GET"])
@login_required
def protected():
    return Response(response="Hello Protected World!", status=200)


@app.route('/<path:resource>')
def serveStaticResource(resource):
    return send_from_directory('static/', resource)


if __name__ == '__main__':
    app.run()
