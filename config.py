import os
basedir = os.path.abspath(os.path.dirname(__file__))

# Connect to the database
class CustomConfig:
    SECRET_KEY = os.urandom(32)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # TODO IMPLEMENT DATABASE URL
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:postgres@127.0.0.1:5432/fyyur'
    DEBUG = True



