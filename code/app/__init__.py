import os

from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# app initialization
application = Flask(__name__)
application.secret_key = os.urandom(24)  # for CSRF

# config and initialize a db
application.config.from_object(Config)
db = SQLAlchemy(application)
db.create_all()
db.session.commit()


from app import routes
from app import classes



