import os

from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
# from flask_bootstrap import Bootstrap

# app initialization
application = Flask(__name__)
# bootstrap = Bootstrap(application)
application.secret_key = os.urandom(24)  # for CSRF
application.secret_key = bytearray([1] * 24)

# config and initialize a db
application.config.from_object(Config)
db = SQLAlchemy(application)
db.create_all()
db.session.commit()

# config login manager
login_manager = LoginManager()
login_manager.init_app(application)

from app import routes
from app import classes

preds = classes.Pred_Results.query.filter_by(path_to_img='20/prediction/1557258655_iStock-5078775151900.jpg').delete()
preds = classes.Pred_Results.query.filter_by(path_to_img='20/prediction/1557258673_iStock-5078775151900.jpg').delete()
preds = classes.Pred_Results.query.filter_by(path_to_img='20/prediction/1557258864_iStock-5078775151900.jpg').delete()
preds = classes.Pred_Results.query.filter_by(path_to_img='20/prediction/1557261814_download_6.jpeg').delete()
preds = classes.Pred_Results.query.filter_by(path_to_img='20/prediction/1557263056_glass.jpg').delete()
db.session.commit()
preds = classes.Pred_Results.query.all()
for pred in preds:
    print(pred.project_id, pred.path_to_img, pred.label)
# kill -9 `ps aux |grep gunicorn |grep app | awk '{ print $2 }'`
