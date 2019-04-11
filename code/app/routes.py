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

# # FORMS
# class RegistrationForm(FlaskForm):
#     username = TextField('Username', validators=[DataRequired()])
#     email = TextField('Email')#, validators=[DataRequired()])
#     companyname = TextField('Company Name')
#     password = PasswordField('Password')#, validators=[DataRequired()])
#     submit = SubmitField('Submit')

# class SigninForm(FlaskForm):
# 	username = TextField('Username', validators=[DataRequired()])
# 	password = PasswordField('Password')#, validators=[DataRequired()])
# 	submit = SubmitField('Submit')

class ProjectForm(FlaskForm):
	project_name = TextField('Project Name', validators=[DataRequired()])
	labels = TextField('Labels', validators=[DataRequired()])
	submit = SubmitField('Submit')


@application.route('/home')
@application.route('/index')
@application.route('/')
def index():
	"""Route to the home page which can be accessed at 
	/ or /index or /home."""
	return render_template("index.html")


@application.route('/blog')
def blog():
	"""Route to the blog page."""
	return render_template("blog.html")


@application.route('/blog-details')
def blog_details():
	"""Route to the blog details page."""
	return render_template("blog-details.html")


@application.route('/contact')
def contact():
	"""Route to the statis page about contact information."""
	return render_template("contact.html")


@application.route('/feature')
def feature():
	"""Route to the statis page about service information."""
	return render_template("feature.html")


@application.route('/pricing')
def pricing():
	"""Route to the statis page listing pricing information."""
	return render_template("pricing.html")


@application.route('/register', methods=['GET', 'POST'])
def register():
	"""
	This function uses method request to take user-input data from a regular
	html form (not a FlaskForm object) then inserts the information of a
	new user into the database using SQLAlchemy.
	If data is valid, dedirect to log in page.
	Oherwise, render the sign up form again.
	"""
	if request.method == "POST":
		username = request.form['username']
		companyname = request.form['companyname']
		email = request.form['email']
		password = request.form['password']

		user_count = classes.User.query.filter_by(username=username).count() + \
			classes.User.query.filter_by(email=email).count()

		if user_count == 0:
			user = classes.User(username, email, companyname, password)
			db.session.add(user)
			db.session.commit()
			return redirect(url_for('signin'))

	return render_template("signup_3.html")


@application.route('/signin', methods=['GET', 'POST'])
def signin():
	"""
	This function uses method request to take user-input data from a regular
	html form (not a FlaskForm object) then queries user information in the database 
	to log user in.
	If user information is found, redirect the user to project page.
	Otherwise, render the sign in form again.
	"""
	if request.method == 'POST':
		username = request.form['username']
		password = request.form['password']
		user = classes.User.query.filter_by(username=username).first()

		if user is not None and user.check_password(password):
			login_user(user)
			return redirect(url_for('projects'))

	return render_template("signin_3.html")


# how would I make this work for adding projects?
# an if statement that checks if it's POST?
@application.route('/projects', methods=['GET', 'POST'])
@login_required
def projects():
	"""
	This route displays the projects of a given user
	and allows them the ability to add a project.
	If a project using the same project_name already exists,
	this will display an error to tell the user 
	to pick another project name.
	"""
	form = ProjectForm()

	if request.method == 'GET':	
		projects = classes.User_Project.query.filter_by(user_id=int(current_user.id)).all()
		return render_template('projects.html', projects=list(projects))
	elif request.method == 'POST':
		project_name = form.project_name.data
		labels = form.labels.data.split(',') 

		# query the Project table 
		# to see if the project already exists
		# if it does, tell the user
		# to pick another project_name
		projects_with_same_name = classes.User_Project.query.filter_by(project_name=project_name).all()
		if len(projects_with_same_name) > 0:
			return f"<h1> A project with the name: {project_name}" + \
				" already exists. Please choose another name for your project."
		else:
			# insert into the Project table
			db.session.add(classes.Project(project_name, current_user.id))
			
			# get the project for the current user that was just added 
			# (by using the creation date)
			most_recent_project = classes.Project.query.filter_by(project_owner_id=current_user.id)\
							.order_by(classes.Project.project_creation_date.desc()).first()

			# insert into the User_Project table
			# so that the user is associated with a project
			db.session.add(classes.User_Project(current_user_id, 
										most_recent_project.project_id, 
										project_name))
			
			# TODO: find a way to bulk insert
			# insert all of the labels that the user entered
			for label in labels:
				db.session.add(classes.Label(most_recent_project.project_id,
											label))

			# pass the list of projects (including the new project) 
			# to the page so it can be shown to the user
			projects = classes.User_Project.query.filter_by(user_id=int(current_user.id)).all()
			# only commit the transactions once everything
			# has been entered successfully.
			db.session.commit()
		return render_template('projects.html', projects=list(projects))
		
	
