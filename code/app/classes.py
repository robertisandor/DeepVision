from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash

from app import db, login_manager

from flask_wtf import FlaskForm, RecaptchaField
from flask_wtf.file import FileField, FileRequired
from wtforms import SubmitField
from werkzeug import secure_filename

from wtforms import StringField, TextField
from wtforms.validators import DataRequired, Email, Length
from sqlalchemy.schema import ForeignKey


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    companyname = db.Column(db.String(80), nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)

    def __init__(self, username, email, companyname, password):
        self.username = username
        self.email = email
        self.companyname = companyname
        self.set_password(password)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Project(db.Model):
    project_id = db.Column(db.Integer, primary_key=True, unique=True, autoincrement=True)
    project_owner_id = db.Column(db.Integer, nullable=False)
    project_creation_date = db.Column(db.DateTime, nullable=False)

    def __init__(self, project_name, project_owner_id):
        self.project_name = project_name
        self.project_owner_id = project_owner_id
        self.project_creation_date = datetime.utcnow()


class Label(db.Model):
    label_id = db.Column(db.Integer, primary_key=True, unique=True, autoincrement=True)
    project_id = db.Column(db.Integer, ForeignKey(Project.project_id), nullable=False)
    label_name = db.Column(db.String(80), nullable=False)
    
    def __init__(self, project_id, label_name):
        self.project_id = project_id
        self.label_name = label_name


class User_Project(db.Model):
    user_id = db.Column(db.Integer, ForeignKey(User.id), primary_key=True, nullable=False)
    project_id = db.Column(db.Integer, ForeignKey(Project.project_id), primary_key=True, nullable=False)
    project_name = db.Column(db.String(80), unique=True, nullable=False)
    
    def __init__(self, user_id, project_id, project_name):
        self.user_id = user_id
        self.project_id = project_id
        self.project_name = project_name

######




db.create_all()
db.session.commit()

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))
