import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']


class ProductionConfig(Config):
    pass


class StagingConfig(Config):
    pass


class DevelopmentConfig(Config):
    pass
