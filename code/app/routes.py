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

class ProjectForm(FlaskForm):
	project_name = TextField('Project Name', validators=[DataRequired()])
	labels = TextField('Labels', validators=[DataRequired()])
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
			return redirect(url_for('index'))
	error_message = "Either wrong format or user already exists."
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
			# return '<h1> Logged in : ' + username + '</h1>'
			return redirect(url_for('projects'))

	return render_template("signin_2.html", form=form)

# how would I make this work for adding projects?
# an if statement that checks if it's POST?
@application.route('/projects', methods=['GET', 'POST'])
@login_required
def projects():
	# how do I get the user info?
	# get_id
	current_user_id = 1
	#current_user_name = 'test'
	form = ProjectForm()
	if request.method == 'GET':	
		projects = classes.User_Project.query.filter_by(user_id=int(current_user_id)).all()
		#projects = classes.User_Project.query.filter_by(user_name=current_user_name)
		print(type(projects), projects)
		return render_template('projects.html', projects=list(projects))
	elif request.method == 'POST':
		project_name = form.project_name.data
		labels = form.labels.data.split(',') 
		print(labels)
		db.session.add(classes.Project(project_name, current_user_id))
		
		# get the most recent project added
		most_recent_project = classes.Project.query.filter_by(project_owner_id=current_user_id)\
						.order_by(classes.Project.project_creation_date.desc()).first()

		#most_recent_project = classes.User_Project.query.filter_by(user_id=int(current_user_id))
		print(most_recent_project.project_creation_date)
		db.session.add(classes.User_Project(current_user_id, 
					   				most_recent_project.project_id, 
					   				project_name))
		for label in labels:
			db.session.add(classes.Label(most_recent_project.project_id,
										label))
		projects = classes.User_Project.query.filter_by(user_id=int(current_user_id)).all()
		db.session.commit()
		return render_template('projects.html', projects=projects)
		
	
