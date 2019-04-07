
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash

from app import db

from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, TextField
from wtforms.validators import DataRequired, Email, Length

# class SignUpForm(FlaskForm):
# 	username = StringField('Username', validators=[DataRequired()])
# 	email = StringField()
# 	password = PasswordField()
# 	recaptcha = RecaptchaField()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.set_password(password)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

db.create_all()
db.session.commit()


	