import os
basedir = os.path.abspath(os.path.dirname(__file__))

class TestConfig:
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/auth.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
