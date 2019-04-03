import os
basedir = os.path.abspath(os.path.dirname(__file__))

class TestConfig:
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:welcome123@10.174.112.100:3306/auth',
    SQLALCHEMY_TRACK_MODIFICATIONS = False
