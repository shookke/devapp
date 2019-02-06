import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'Ir$aGXbhgHrTKxs9GCvG0Bt3y'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

    ADMINS = ['kevin@nsyncdata.net']
    ADMPW = 'j6b4a8krG3iXpN3'

    JENKINS_URL = 'http://dev.nsyncdata.net:8080'
    JENKINS_TOKEN = '11b43739274d46ac9fe24ded95c86c901e'

    HOST_ADDRESS = '10.200.11.6'
    UPLOAD_PATH = '/var/build/'

    SECURITY_PASSWORD_SALT = 'ay7k3gN1BKhgIOSLRL5QSgvee'