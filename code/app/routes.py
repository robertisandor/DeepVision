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
    username = TextField('Username', validators=[DataRequired()])
    email = TextField('Email')#, validators=[DataRequired()])
    password = PasswordField('Password')#, validators=[DataRequired()])
    submit = SubmitField('Submit')

class SigninForm(FlaskForm):
	username = TextField('Username', validators=[DataRequired()])
	password = PasswordField('Password')#, validators=[DataRequired()])
	submit = SubmitField('Submit')


@application.route('/home')
@application.route('/index')
@application.route('/')
def index():
    return render_template("index.html")


@application.route('/blog')
def blog():
    return render_template("blog.html")


@application.route('/blog-details')
def blog_details():
    return render_template("blog-details.html")


@application.route('/contact')
def contact():
    return render_template("contact.html")


@application.route('/feature')
def feature():
    return render_template("feature.html")


@application.route('/pricing')
def pricing():
    return render_template("pricing.html")


@application.route('/register', methods=['GET', 'POST'])
def register():
	form = RegistrationForm()
	if request.method == "POST" and form.validate():
		username = form.username.data
		password = form.password.data
		email = form.email.data

		user_count = classes.User.query.filter_by(username=username).count() + \
			classes.User.query.filter_by(email=email).count()

		if user_count == 0:
			user = classes.User(username, email, password)
			db.session.add(user)
			db.session.commit()
			# return ('<h1> Registered : ' + username + '</h1>')
			return redirect(url_for('index'))
	# error_message = "Either wrong format or user already exists."
	return render_template("signup_2.html", form=form, error_message=error_message)


@application.route('/signin', methods=['GET', 'POST'])
def signin():
	form = SigninForm()
	if request.method == "POST" and form.validate():
		username = form.username.data
		password = form.password.data
		user = classes.User.query.filter_by(username=username).first()

		if user is not None and user.check_password(password):
			login_user(user)
			return '<h1> Logged in : ' + username + '</h1>'
			# return redirect(url_for('project'))

	return render_template("signin_2.html", form=form)


