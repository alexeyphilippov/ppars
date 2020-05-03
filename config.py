class BaseConfig(object):
    DEBUG = False
    TESTING = False
    JSON_AS_ASCII = False


class Development(BaseConfig):
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = None
    SQLALCHEMY_TRACK_MODIFICATIONS = False
