import os
from app import application, classes, db

from flask import (render_template,
                   redirect,
                   url_for,
                   request,
                   flash,
                   jsonify)

import json
import boto3
from flask_wtf.file import FileField, FileRequired
import matplotlib.image as mpimg
import tempfile
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

# for prediction
import numpy as np
from ml import train, predict

# Web app backend ##############


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

        user_count = classes.User.query.filter_by(username=username).count() \
            + classes.User.query.filter_by(email=email).count()

        if user_count == 0:
            user = classes.User(username, email, companyname, password)
            db.session.add(user)
            db.session.commit()
            # flash('successfully logged in.')
            return redirect(url_for('signin'))
        else:
            flash('Username or email already exists.')

    return render_template("signup.html")


@application.route('/signin', methods=['GET', 'POST'])
def signin():
    """
    This function uses method request to take user-input data from a regular
    html form (not a FlaskForm object) then queries user information in the
    database to log user in.
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
        else:
            flash('Invalid username and password combination.')

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
    Project details are listed in a table, allowing user to
    upload image data per project, per label, to initiate
    training process and to upload new image for prediction.
    """
    if request.method == 'GET':
        users_projects = classes.User_Project.query.filter_by(user_id=current_user.id).all()
        project_ids = [user_project.project_id for user_project in users_projects]
        projects = classes.Project.query.filter(classes.Project.project_id.in_(project_ids))

        # return objects to easily call by attribute names,
        # rather than by indexes, please keep
        proj_labs = {}
        for proj in projects:
            proj_labs[proj.project_id] = classes.Label.query.filter_by(
                project_id=proj.project_id).all()
        # use dictionary to easily call by key which matches the ids,
        # more secure than by indexes, please keep

        return render_template('projects.html', projects=projects,
                               proj_labs=proj_labs)

    elif request.method == 'POST':
        project_name = request.form['project_name']
        labels = [label.strip() for label in request.form['labels'].split(',')]

        # this was updated
        if len(set(labels)) != len(labels):
            return f"<h1>There are duplicate labels. Please enter labels that are different.</h1>"
        # TODO: verify label_names to be unique within one project,
        # TODO: right now can have same name but different labelid.

        # query the Project table to see if the project already exists
        # if it does, tell the user to pick another project_name
        users_projects = classes.User_Project.query.filter_by(user_id=current_user.id).all()
        project_ids = [user_project.project_id for user_project in users_projects]

        # if a user has multiple projects
        # check if the project name with the same name already exists for them
        projects_with_same_name = []
        if len(users_projects) > 0:
            projects = classes.Project.query.filter_by(project_name=project_name).all()
            projects_with_same_name = [project.project_id for project in projects if project.project_id in project_ids]

        if len(projects_with_same_name) > 0:
            return f"<h1> A project with the name: {project_name}" + \
                   " already exists. Please choose another " \
                   "name for your project.</h1>"
        else:
            # insert into the Project table
            db.session.add(classes.Project(project_name, int(current_user.id)))

            # get the project for the current user that was just added
            # (by using the creation date)
            most_recent_project = classes.Project.query \
                .filter_by(project_owner_id=current_user.id) \
                .order_by(classes.Project.project_creation_date.desc()).first()
            print(most_recent_project.project_name)

            # insert into the User_Project table
            # so that the user is associated with a project
            db.session.add(classes.User_Project(int(current_user.id),
                                                most_recent_project.project_id))

            # TODO: find a way to bulk insert
            # insert all of the labels that the user entered
            for label in labels:
                db.session.add(classes.Label(most_recent_project.project_id,
                                             label))

            most_recent_project_labels = classes.Label.query.filter_by(project_id=most_recent_project.project_id)

            # this was added
            # TODO: when creating the project, I need to create the model 
            # and prediction folders for a given project in S3 

            # TODO: abstract writing to S3 bucket into a function; 
            # remove duplicated code
            bucket_name = 'msds603-deep-vision'
            s3_connection = boto.connect_s3(
                aws_access_key_id='AKIAIQRI4EE5ENXNW6LQ',
                aws_secret_access_key='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')
            # to be fixed with paramiko
            bucket = s3_connection.get_bucket(bucket_name)
            k = Key(bucket)

            for label in most_recent_project_labels:
                k.key = f'/{str(most_recent_project.project_id)}/{str(label.label_id)}/'
                k.set_contents_from_string('')

            k.key = f'/{str(most_recent_project.project_id)}/model/'
            k.set_contents_from_string('')

            k.key = f'/{str(most_recent_project.project_id)}/prediction/'
            k.set_contents_from_string('')

            # create folder in predict bucket
            bucket_name = 'msds603-deep-vision-predict'
            s3_connection = boto.connect_s3(
                aws_access_key_id='AKIAIQRI4EE5ENXNW6LQ',
                aws_secret_access_key='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')
            # to be fixed with paramiko
            bucket = s3_connection.get_bucket(bucket_name)
            k = Key(bucket)

            k.key = f'/{str(most_recent_project.project_id)}/'
            k.set_contents_from_string('')

            # pass the list of projects (including the new project) to the page
            # so it can be shown to the user
            # only commit the transactions once everything has been entered.
            db.session.commit()
            
            users_projects = classes.User_Project.query.filter_by(user_id=current_user.id).all()
            project_ids = [user_project.project_id for user_project in users_projects]
            projects = classes.Project.query.filter(classes.Project.project_id.in_(project_ids))
            
            proj_labs = {}
            for proj in projects:
                proj_labs[proj.project_id] = classes.Label.query.filter_by(
                    project_id=proj.project_id).all()

            return render_template('projects.html', projects=projects,
                                   proj_labs=proj_labs)


class UploadFileForm(FlaskForm):
    """Class for uploading multiple files when submitted"""
    file_selector = MultipleFileField('File')
    submit = SubmitField('Submit')


@application.route('/upload/<labid>', methods=['GET', 'POST'])
@login_required
def upload(labid):
    """
    This route allows users to bulk upload image data per project, per label.
    Files would be stored in S3 bucket organized as "./project/label/files".
    """
    label = classes.Label.query.filter_by(label_id=labid).first()
    labelnm = label.label_name
    projid = label.project_id
    # labelnm = classes.Label.query.filter_by(label_id=labid).first().label_name
    # projid = classes.Label.query.filter_by(label_id=labid).first().project_id

    projnm = classes.Project.query.filter_by(project_id=projid) \
        .first().project_name
    # projnm = classes.User_Project.query.filter_by(project_id=projid) \
    #     .first().project_name

    form = UploadFileForm()
    if form.validate_on_submit():
        files = form.file_selector.data
        for f in files:
            tmp = tempfile.NamedTemporaryFile()
            file_content = ''
            # file must be temporarily created
            # so that it can be read
            # to find out the aspect ratio of the image
            with open(tmp.name, 'wb') as data:
                file_content = f.stream.read()
                data.write(file_content)
            # TODO: rename the images to be unique per project
            # and based on the count of images already stored
            # so that if you upload the same image multiple times 
            # there will be multiple copies with different filenames
            # rather than updating the same file
            image = mpimg.imread(tmp.name)
            aspect_ratio = round(float(image.shape[1]) / float(image.shape[0]), 1)
            filename = secure_filename(f.filename)
            # I need to find the aspect ratio of the image
            # then query
            # and insert that into the table in postgres

            aspect_ratios = classes.Aspect_Ratio.query.filter_by(project_id=projid).filter_by(aspect_ratio=str(aspect_ratio)).all()
            # aspect_ratios = classes.Aspect_Ratio.query.filter_by(project_id=projid).all()
            # aspect_ratios = classes.Aspect_Ratio.query.all()
            
            if len(aspect_ratios) == 0:
                db.session.add(classes.Aspect_Ratio(projid, str(aspect_ratio), 1))
            elif len(aspect_ratios) == 1:
                aspect_ratios[0].count += 1

            db.session.commit()

            bucket_name = 'msds603-deep-vision'
            s3_connection = boto.connect_s3(
                aws_access_key_id='AKIAIQRI4EE5ENXNW6LQ',
                aws_secret_access_key='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')
            # to be fixed with paramiko
            bucket = s3_connection.get_bucket(bucket_name)
            k = Key(bucket)
            k.key = '/'.join([str(projid), str(labid), filename])
            k.set_contents_from_string(file_content)

        # I think I need to insert/update the table
        # with the newest aspect ratio

        return redirect(url_for('projects'))
    return render_template('upload_lab.html', projnm=projnm,
                           labelnm=labelnm, form=form)


@application.route('/train/<projid>', methods=['GET', 'POST'])
@login_required
def train(proj_id):
    """
    This route triggered when a user clicks "Train" button in a project.
    After training is done, the user will receive an notification email.
    """
    # query inputs for to train the model
    proj = classes.Project.query.filter_by(project_id=proj_id).first()
    project_name = proj.project_name
    last_asp_ratio = proj.last_train_asp_ratio
    
    project_owner_id = proj.project_owner_id
    proj_owner = classes.User.query.filter_by(id=project_owner_id).first() 
    proj_owner_name = proj_owner.username
    proj_owner_email = proj_owner.email

    labels = classes.Label.query.filter_by(project_id=projid).all()
    lbl2idx = {label.label_name: label.label_index for label in labels}

    # call the train function from ml module
    train(proj_name, last_asp_ratio, proj_owner_name, proj_owner_email, lbl2idx)



@application.route('/predict/<projid>', methods=['GET', 'POST'])
@login_required
def predict(projid):
    """
    This route provides prediction on newly uploaded image for a project.
    :return: predicted label of the new image, display on the website.
    """
    projnm = classes.Project.query.filter_by(project_id=projid) \
        .first().project_name
    form = UploadFileForm()
    pred_lab = ''
    if form.validate_on_submit():
        files = form.file_selector.data
        
        # simply get the aspect ratio and the project id 
        
        # train(projid, current_project.project_owner_id, project_owner.username, project_owner.email)
        # pojectid, paths, aspect ratio
        client = boto3.client('s3', aws_access_key_id='AKIAIQRI4EE5ENXNW6LQ',
                aws_secret_access_key='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')
        bucket_name = 'msds603-deep-vision'
        filepaths = client.list_objects(Bucket=bucket_name, Prefix=projid, Delimiter='')
        filepaths = [item['Key'] for item in filepaths['Contents'] if len(item['Key'].split('.')) > 1]
        print(filepaths)

        # to get aspect_ratio
        project = classes.Project.query.filter_by(project_id=projid).first()
        aspect_ratio = project.last_train_asp_ratio
        if aspect_ratio is None:
            aspect_ratio = 1
        print(aspect_ratio)

        # to get number of training labels
        labels = classes.Label.query.filter_by(project_id=projid).all()
        print(len(labels))

        # predict(project_id=projid, paths=filepaths, aspect_r=aspect_ratio, n_training_labels=len(labels))
        
        # figure out issue with labels
        # label history

        for f in files:
            filename = secure_filename(f.filename)
            file_content = f.stream.read()

            
            s3_connection = boto.connect_s3(
                aws_access_key_id='AKIAIQRI4EE5ENXNW6LQ',
                aws_secret_access_key='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')
            # to be fixed with paramiko
            bucket = s3_connection.get_bucket(bucket_name)
            k = Key(bucket)
            k.key = '/'.join([str(projid), 'prediction', filename])
            k.set_contents_from_string(file_content)

    return render_template('predict.html', projnm=projnm,
                           pred_lab=pred_lab, form=form, projid=projid)


@application.route('/status/<projid>', methods=['GET', 'POST'])
@login_required
def status(projid):
    """
    This route provides project status, 
    including the prediction results and users of this project.
    :return: model prediction results and users of the project.
    """
    projnm = classes.Project.query.filter_by(project_id=projid) \
        .first().project_name
    userids_of_one_project = classes.User_Project.query \
        .filter_by(project_id=projid).all()
    users = []
    for user_proj in userids_of_one_project:
        users.append(classes.User.query.filter_by(
            id=user_proj.user_id).first().username)
    if request.method == "POST":
        username = request.form['username']
        count = classes.User.query.filter_by(username=username).count()
        if count == 0:
            flash('User does not exist.')
        elif username in users:
            flash(username + ' already exists.')
        else:
            user_id = classes.User.query.filter_by(username=username) \
                .first().id
            user_proj = classes.User_Project(user_id, projid)
            db.session.add(user_proj)
            db.session.commit()
            return render_template('status.html', projnm=projnm, 
                           users=users, projid=projid)
    return render_template('status.html', projnm=projnm, 
                           users=users, projid=projid)


@application.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@application.errorhandler(401)
def unauthorized(e):
    """If user goes to a page that requires authorization such as
    projects page but is not yet logged in, redirect them to
    the log-in page."""
    return redirect(url_for('signin'))


# Mobile app backend ##############


@application.route('/mobile_register', methods=['GET', 'POST'])
def mobile_register():
    """
    This function uses method post to register user information
    in the data base. This returns a message indicating the if
    the procedure has been successful or not.

    :return: return dictionary with success "1"/"0" if success/failure
    """
    if request.method == "POST":
        username = request.form['username']
        companyname = request.form['companyname']
        email = request.form['email']
        password = request.form['password']

        user_count = classes.User.query.filter_by(username=username).count() \
            + classes.User.query.filter_by(email=email).count()

        if user_count == 0:
            user = classes.User(username, email, companyname, password)
            db.session.add(user)
            db.session.commit()
            # return "1" #
            return json.dumps({"success": "1"})

    # return "0"
    return json.dumps({"success": "0"})


@application.route('/mobile_signin', methods=['GET', 'POST'])
def mobile_signin():
    """
    Mobile version of signin
    This function uses method post to take user-input data and check if exists
    and the credentials are correct.

    :return: return dictionary with success "1"/"0" if success/failure
    """
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = classes.User.query.filter_by(email=email).first()

        if user is not None and user.check_password(password):
            login_user(user)
            # return "1"
            return json.dumps({"success": "1"})

    # return "0"
    return json.dumps({"success": "0"})


@application.route('/mobile_projects', methods=['GET', 'POST'])
@login_required
def mobile_projects():
    """
     This route is the backend for the project menu of a
     given user in the mobile phone.
     It allows for projects to be added.
     If a project using the same project_name already exists,
     this will display an error to tell the user
     to pick another project name.

     :return: return dictionary with success "1"/"0" if
    success/failure and the list of projects
     """
    if request.method == 'GET':
        projects = classes.User_Project.query.filter_by(
            user_id=int(current_user.id)).all()
        # return objects to easily call by attribute names,
        # rather than by indexes, please keep
        proj_labs = {}
        for proj in projects:
            proj_labs[proj.project_id] = classes.Label.query.filter_by(
                project_id=proj.project_id).all()
        # use dictionary to easily call by key which matches the ids,
        # more secure than by indexes, please keep

        # return render_template('projects.html', projects=projects,
        # proj_labs=proj_labs)
        return json.dumps(
            {"success": "1", "projects": json.dumps(projects),
             "proj_labs": json.dumps(proj_labs)})

    elif request.method == 'POST':
        project_name = request.form['project_name']
        labels = [label.strip() for label in request.form['labels'].split(',')]

        # TODO: verify label_names to be unique within one project,
        # right now can have same name but different labelid.

        # query the Project table to see if the project already exists
        # if it does, tell the user to pick another project_name
        projects_with_same_name = classes.User_Project.query.filter_by(
            project_name=project_name).all()
        if len(projects_with_same_name) > 0:
            # return f"<h1> A project with the name: {project_name}" + \
            #        " already exists. Please choose
            # another name for your project."
            return json.dumps({"success": "0"})
        else:
            # insert into the Project table
            db.session.add(classes.Project(project_name, int(current_user.id)))

            # get the project for the current user that was just added
            # (by using the creation date)
            most_recent_project = classes.Project.query.filter_by(
                project_owner_id=current_user.id) \
                .order_by(classes.Project.project_creation_date.desc()).first()

            # insert into the User_Project table so that the
            # user is associated with a project
            db.session.add(classes.User_Project(int(current_user.id),
                                                most_recent_project.project_id,
                                                project_name))

            # TODO: find a way to bulk insert
            # insert all of the labels that the user entered
            for label in labels:
                db.session.add(classes.Label(most_recent_project.project_id,
                                             label))

            # pass the list of projects (including the new project)
            # to the page so it can be shown to the user
            # only commit the transactions once everything
            # has been entered successfully.
            db.session.commit()

            projects = classes.User_Project.query.filter_by(user_id=int(
                current_user.id)).all()
            proj_labs = {}
            for proj in projects:
                proj_labs[proj.project_id] = classes.Label.query.filter_by(
                    project_id=proj.project_id).all()

            # return render_template('projects.html',
            # projects=projects, proj_labs=proj_labs)
            return json.dumps(
                {"success": "1", "projects": json.dumps(projects),
                 "proj_labs": json.dumps(proj_labs)})


@application.route('/mobile_logout')
@login_required
def mobile_logout():
    '''
    Log out function for mobile phone
    :return: return dictionary with success "1"/"0" if success/failure
    '''
    logout_user()
    # flash('You have been logged out.')
    # return "1"
    return json.dumps({"success": "1"})

# TODO: mobile_upload
