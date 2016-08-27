import os
from datetime import datetime
from flask import Flask, request, Response, flash, url_for, redirect, \
     render_template, abort, send_from_directory
from flask.ext.login import LoginManager, UserMixin, login_required

app = Flask(__name__)
app.config.from_pyfile('flaskapp.cfg')

login_manager = LoginManager()
login_manager.init_app(app)
#login_manager.login_view = 'login'

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


@login_manager.request_loader
def load_user(request):
    token = request.headers.get('Authorization')
    if token is None:
        token = request.args.get('token')

    if token is not None:
        username,password = token.split(":") # naive token
        user = User.get(username)
        if user and user.password == password:
            return user
    return None


@app.route("/", methods=["GET"])
def index():
    return Response(response="Hello World!", status=200)


@app.route("/protected/", methods=["GET"])
@login_required
def protected():
    return Response(response="Hello Protected World!", status=200)


#@app.route('/')
#def index():
#    return render_template('index.html')

@app.route('/<path:resource>')
def serveStaticResource(resource):
    return send_from_directory('static/', resource)


if __name__ == '__main__':
    app.run()
