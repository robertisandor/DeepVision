import os
from app import application, classes, db

from flask import render_template, redirect, url_for, request

# for building forms
from flask_wtf import FlaskForm#, RecaptchaField
from wtforms import SubmitField
from wtforms import TextField, PasswordField
from wtforms.validators import DataRequired, Email, Length

# for handling log-in, log-out states
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash
from flask_login import current_user, login_user, login_required, logout_user

# FORMS
class RegistrationForm(FlaskForm):
    username = TextField('Username')#, validators=[DataRequired()])
    email = TextField('Email')#, validators=[DataRequired()])
    password = PasswordField('Password')#, validators=[DataRequired()])
    submit = SubmitField('Submit')


@application.route('/home')
@application.route('/')
def index():
    return render_template("index.html")


@application.route('/register', methods=['GET', 'POST'])
def register():
	form = RegistrationForm()
	if form.validate_on_submit():
		username = form.username.data
		password = form.password.data
		email = form.email.data
		user = classes.User(username, email, password)
		db.session.add(user)
		db.session.commit()
		return '<h1> Registered : ' + username + '</h1>'
	return render_template("signup_2.html", form=form)


# class RegistrationForm(Form):
#     username = TextField('Username', [validators.Length(min=4, max=20)])
#     email = TextField('Email Address', [validators.Length(min=6, max=50)])
#     password = PasswordField('New Password', [
#         validators.Required(),
#         validators.EqualTo('confirm', message='Passwords must match')
#     ])
#     confirm = PasswordField('Repeat Password')


# class RegistrationForm(FlaskForm):
#     username = TextField('Username', validators=[DataRequired()])
#     email = TextField('Email', validators=[DataRequired()])
#     password = PasswordField('Password', validators=[DataRequired()])
#     # recaptcha = RecaptchaField()
#     submit = SubmitField('Submit')

# @application.route("/register", methods=['GET', 'POST'])
# def sign_up():
#     # form = SignUpForm()
#     form = RegistrationForm()
#     if form.validate():
#         username = form.username.data
#         password = form.password.data
#         email = form.email.data
#         return f"signed up: {username}"
#     return render_template("signup.html", form=form)


# class SignUpForm(FlaskForm):
# 	username = StringField('Username', validators=[DataRequired()])
# 	email = StringField('Email', validators=[DataRequired()])
# 	password = PasswordField('Password', validators=[DataRequired()])
# 	recaptcha = RecaptchaField()


# @application.route('/signup')
# def register():
#     username = 'diane'
#     password = 'pwd'
#     email='diane@gmail.com'

#     user = classes.User(username, email, password)
#     db.session.add(user)
#     db.session.commit()

#     return '<h1> Registered : ' + username + '</h1>'


