"""Configurations."""
import os
basedir = os.path.abspath(os.path.dirname(__file__))

DATABASE_NAME = "homework_db"


class Config:
    """Base Config Object containing settings that should always be present."""

    SECRET_KEY = os.environ.get('SECRET_KEY', "this_needs_to_be_more_secure")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SERVICE_NAME = 'homework'
    K8S_SERVICE_NAME = 'VLE_HOMEWORK'


class Development(Config):
    """Config used in development."""

    DEBUG = True
    PG_PASSWORD = 'postgres'
    PG_HOST = 'db'
    PG_USER = 'postgres'
    SQLALCHEMY_DATABASE_URI = 'postgresql://{}:{}@{}/{}'.format(
        PG_USER, PG_PASSWORD, PG_HOST, DATABASE_NAME)


class Testing(Config):
    """Config used when running unit tests."""

    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(
        basedir, 'testing-database.sqlite')
    PRESERVE_CONTEXT_ON_EXCEPTION = False
    NO_REGISTER = True


class Migrations(Development):
    """Used to run migrations on docker-compose."""

    NO_REGISTER = True


class Minikube(Config):
    DEBUG = True
    PG_PASSWORD = os.environ.get('POSTGRES_PASSWORD', 'postgres')
    PG_HOST = os.environ.get('POSTGRES_HOST', 'killer-gibbon-postgresql')
    PG_USER = os.environ.get('POSTGRES_USER', 'postgres')
    SQLALCHEMY_DATABASE_URI = "postgresql://{}:{}@{}/{}".format(
        PG_USER, PG_PASSWORD, PG_HOST, DATABASE_NAME)


config = {
    'development': Development,
    'testing': Testing,
    'minikube': Minikube,
    'migrations':  Migrations,
    'default': Development
}
