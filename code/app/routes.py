import os
from app import application, classes, db

from flask import (render_template,
                   redirect,
                   url_for,
                   request,
                   flash,
                   jsonify)

import json

from flask_wtf.file import FileField, FileRequired
from wtforms import SubmitField
from werkzeug import secure_filename

# for building forms
from flask_wtf import FlaskForm  # RecaptchaField
from wtforms import SubmitField, MultipleFileField
from wtforms import TextField, PasswordField
from wtforms.validators import DataRequired, Email, Length

# for handling log-in, log-out states
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash
from flask_login import current_user, login_user, login_required, logout_user

# for upload to s3
from boto.s3.key import Key
import boto
########### Web app backend ##############


@application.route('/home')
@application.route('/index')
@application.route('/')
def index():
    """
    Route to the home page which can be accessed at / or /index or /home.
    """
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

    return render_template("signup.html")


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

    return render_template("signin.html")

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
    if request.method == 'GET':
        projects = classes.User_Project.query.filter_by(user_id=int(current_user.id)).all()
        # return objects to easily call by attribute names, rather than by indexes, please keep
        proj_labs = {}
        for proj in projects:
            proj_labs[proj.project_id] = classes.Label.query.filter_by(project_id=proj.project_id).all()
        # use dictionary to easily call by key which matches the ids, more secure than by indexes, please keep

        return render_template('projects.html', projects=projects, proj_labs=proj_labs)

    elif request.method == 'POST':
        project_name = request.form['project_name']
        labels = [label.strip() for label in request.form['labels'].split(',')]

        # TODO: verify label_names to be unique within one project, right now can have same name but different labelid.

        # query the Project table to see if the project already exists
        # if it does, tell the user to pick another project_name
        projects_with_same_name = classes.User_Project.query.filter_by(project_name=project_name).all()
        if len(projects_with_same_name) > 0:
            return f"<h1> A project with the name: {project_name}" + \
                " already exists. Please choose another name for your project."
        else:
            # insert into the Project table
            db.session.add(classes.Project(project_name, int(current_user.id)))

            # get the project for the current user that was just added
            # (by using the creation date)
            most_recent_project = classes.Project.query.filter_by(project_owner_id=current_user.id)\
                            .order_by(classes.Project.project_creation_date.desc()).first()

            # insert into the User_Project table so that the user is associated with a project
            db.session.add(classes.User_Project(int(current_user.id),
                                        most_recent_project.project_id,
                                        project_name))

            # TODO: find a way to bulk insert
            # insert all of the labels that the user entered
            for label in labels:
                db.session.add(classes.Label(most_recent_project.project_id,
                                            label))

            # pass the list of projects (including the new project) to the page so it can be shown to the user
            # only commit the transactions once everything has been entered successfully.
            db.session.commit()

            projects = classes.User_Project.query.filter_by(user_id=int(current_user.id)).all()
            proj_labs = {}
            for proj in projects:
                proj_labs[proj.project_id] = classes.Label.query.filter_by(project_id=proj.project_id).all()

            return render_template('projects.html', projects=projects, proj_labs=proj_labs)


class UploadFileForm(FlaskForm):
    """Class for uploading file when submitted"""
    file_selector = MultipleFileField('File')#, validators=[FileRequired()])
    submit = SubmitField('Submit')


@application.route('/upload/<labid>', methods=['GET', 'POST'])
@login_required
def upload(labid):
    labelnm = classes.Label.query.filter_by(label_id=labid).first().label_name
    projid = classes.Label.query.filter_by(label_id=labid).first().project_id
    projnm = classes.User_Project.query.filter_by(project_id=projid).first().project_name

    form = UploadFileForm()
    if form.validate_on_submit():  # Check if it is a POST request and if it is valid.
        files = form.file_selector.data
        for f in files:
            filename = secure_filename(f.filename)
            file_content = f.stream.read()

            bucket_name = 'msds603-deep-vision'
            s3_connection = boto.connect_s3(aws_access_key_id='AKIAIQRI4EE5ENXNW6LQ',
                                            aws_secret_access_key='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')
            bucket = s3_connection.get_bucket(bucket_name)
            k = Key(bucket)
            k.key = '/'.join([str(projid), str(labid), filename])
            k.set_contents_from_string(file_content)
        return redirect(url_for('projects'))
    return render_template('upload_lab.html', projnm=projnm, labelnm=labelnm, form=form)


@application.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('index'))


########### Mobile app backend ##############


@application.route('/mobile_register', methods=['GET', 'POST'])
def mobile_register():
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
            # return "1" #
            return json.dumps(jsonify(success=1))

    # return "0"
    return json.dumps(jsonify(success=0))


@application.route('/mobile_signin', methods=['GET', 'POST'])
def mobile_signin():
    """
    This function uses method request to take user-input data from a regular
    html form (not a FlaskForm object) then queries user information in the database
    to log user in.
    If user information is found, redirect the user to project page.
    Otherwise, render the sign in form again.
    """
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = classes.User.query.filter_by(email=email).first()

        if user is not None and user.check_password(password):
            login_user(user)
            # return "1"
            return json.dumps({"success":"1"})

    # return "0"
    return json.dumps({"success":"0"})


@application.route('/mobile_projects', methods=['GET', 'POST'])
@login_required
def mobile_projects():
    """
    This route displays the projects of a given user
    and allows them the ability to add a project.
    If a project using the same project_name already exists,
    this will display an error to tell the user
    to pick another project name.
    """
    if request.method == 'GET':
        projects = db.session.query(classes.User_Project.project_name).filter_by(user_id=int(current_user.id)).all()
        # return render_template('projects.html', projects=list(projects))
        projects = [proj[0].strip(",") for proj in projects]
        # return json.dumps(projects)
        return json.dumps(jsonify(success=1, projects=json.dumps(projects)))

    elif request.method == 'POST':


        # TODO: Adapt this to the format received from Android
        project_name = request.form['project_name']
        labels = [label.strip() for label in request.form['labels'].split(',')]


        projects_with_same_name = classes.User_Project.query.filter_by(project_name=project_name).all()

        if len(projects_with_same_name) > 0:
            # return json.dumps([])
            return json.dumps(jsonify(success=0))
        else:
            # insert into the Project table
            db.session.add(classes.Project(project_name, int(current_user.id)))

            # get the project for the current user that was just added
            # (by using the creation date)
            most_recent_project = (classes.Project.query
                                   .filter_by(project_owner_id=current_user.id)
                                   .order_by(classes.Project.project_creation_date.desc())
                                   .first()
                                   )

            # insert into the User_Project table so that the user is associated with a project
            db.session.add(classes.User_Project(int(current_user.id),
                                                most_recent_project.project_id,
                                                project_name))

            # TODO: find a way to bulk insert
            # insert all of the labels that the user entered
            for label in labels:
                db.session.add(classes.Label(most_recent_project.project_id,
                                             label))

            # pass the list of projects (including the new project) to the page so it can be shown to the user
            # projects = classes.User_Project.query.filter_by(user_id=int(current_user.id)).all()
            # only commit the transactions once everything has been entered successfully.
            db.session.commit()

            projects = (db.session
                        .query(classes.User_Project.project_name)
                        .filter_by(user_id=int(current_user.id))
                        .all()
                        )

            projects = [proj[0].strip(",") for proj in projects]

            # return  json.dumps(projects)
            return json.dumps(jsonify(success=1, projects=json.dumps(projects)))
            # return render_template('projects.html',
            # 					   projects=[proj[0].strip(",") for proj in projects])


@application.route('/mobile_logout')
@login_required
def mobile_logout():
    logout_user()
    # flash('You have been logged out.')
    # return "1"
    return json.dumps(jsonify(success=1))
