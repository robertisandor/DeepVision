import os
basedir = os.path.abspath(os.path.dirname(__file__))

# config DB
## this is to be changed to make connect with RDB
class Config(object):
    # SQLALCHEMY_DATABASE_URI = 'postgresql://msds603master:msds603master@msds603test.cpk2y02osnmj.us-east-2.rds.amazonaws.com:5432/test'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'week3.db') # for testing on local machine
    SQLALCHEMY_TRACK_MODIFICATIONS = True