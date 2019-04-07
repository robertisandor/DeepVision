import os
basedir = os.path.abspath(os.path.dirname(__file__))

# config DB
## this is to be changed to make connect with RDB
class Config(object):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'deepvision.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = True