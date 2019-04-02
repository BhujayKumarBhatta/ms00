import os
basedir = os.path.abspath(os.path.dirname(__file__))

class TestConfig:
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqldb://root:welcome123@localhost/auth'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
