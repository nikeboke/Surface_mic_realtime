from flask import Flask
from flask_cors import CORS
from app.config import DevConfig, TestConfig
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt


def create_app():
    app = Flask(__name__)
    CORS(app)
    cors = CORS(app, resources={r"/*":{"origins":"*"}})
    app.config.from_object(DevConfig)


    db = SQLAlchemy(app)
    bcrypt = Bcrypt(app)
    login_manager = LoginManager(app)
    login_manager.login_view = 'main.login'

    return app, db, bcrypt, login_manager

app, db, bcrypt, login_manager = create_app()

from app.main.routes import main
from app.apis.data import data
from app.apis.hue import hue
from app.apis.auth import auth
from app.apis.events import events

app.register_blueprint(main)
app.register_blueprint(data)
app.register_blueprint(hue)
app.register_blueprint(auth)
app.register_blueprint(events)


