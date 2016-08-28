import os
from datetime import datetime
from flask import Flask, request, Response, flash, url_for, redirect, \
     render_template, abort, send_from_directory
from flask.ext.login import LoginManager, UserMixin, login_required, login_user

app = Flask(__name__)
app.config.from_pyfile('flaskapp.cfg')

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    # proxy for a database of users
    user_database = {"vidstige": ("Samuel Carlsson", "Abc123"),
               "foobar": ("Foo Bar", "haj")}

    def __init__(self, username, password):
        self.id = username
        self.password = password

    @classmethod
    def get(cls, id):
        user_entry = cls.user_database.get(id)
        if user_entry is  None:
            return None
        return User(id, user_entry[1])


def get_user_for(username, passphrase):
    # Todo also check password
    return load_user(username)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = get_user_for(request.form['username'], request.form['password'])
        if user:
            login_user(user)
            flash("Logged in successfully!", category='success')
            return redirect(request.args.get("next") or url_for("write"))
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
