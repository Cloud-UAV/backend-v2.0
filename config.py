import os

from dotenv import load_dotenv


basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, 'rds_postgres.env'))


DB_USR = os.environ.get('DB_USR')
DB_PWD = os.environ.get('DB_PWD')
DB_ENPOINT = os.environ.get('DB_ENPOINT')
DB_NAME = os.environ.get('DB_NAME')
DB_PORT = os.environ.get('DB_PORT')


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = f'postgres+psycopg2://{DB_USR}:{DB_PWD}@{DB_ENPOINT}:{DB_PORT}/{DB_NAME}'

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # uncomment below to see raw queries
    # SQLALCHEMY_ECHO = True
