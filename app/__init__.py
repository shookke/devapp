from flask import Flask, url_for
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_admin import Admin
from flask_admin import helpers as admin_helpers
from flask_login import LoginManager
from flask_security import Security, SQLAlchemyUserDatastore, current_user
from flask_bootstrap import Bootstrap
from app.model_views import DevappModelView
import logging, os
from logging.handlers import SMTPHandler, RotatingFileHandler


app = Flask(__name__)
    
app.config.from_object(Config)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

login = LoginManager(app)
login.login_view = 'login'

bootstrap = Bootstrap(app)

# Setup Flask-Security
from app.models import User, Role, Container
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

admin = Admin(app, name='devapp', template_mode='bootstrap3')
admin.add_view(DevappModelView(User, db.session))
admin.add_view(DevappModelView(Role, db.session))
admin.add_view(DevappModelView(Container, db.session))

#admin_role = Role(name='superuser')
#db.session.add(admin_role)
#db.session.commit()

admin_init = User(username=app.config['ADMINS'][0]['username'],
                email=app.config['ADMINS'][0]['email'],
                roles='superuser')
admin_init.set_password(app.config['ADMINS'][0]['password'])
db.session.add(admin_init)
db.session.commit()

# define a context processor for merging flask-admin's template context into the
# flask-security views.
@security.context_processor
def security_context_processor():
    return dict(
        admin_base_template=admin.base_template,
        admin_view=admin.index_view,
        h=admin_helpers,
        get_url=url_for
    )

if not app.debug:
    if app.config['MAIL_SERVER']:
        auth = None
        if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
            auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
        secure = None
        if app.config['MAIL_USE_TLS']:
            secure = ()
        mail_handler = SMTPHandler(
            mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
            fromaddr='no-reply@' + app.config['MAIL_SERVER'],
            toaddrs=app.config['ADMINS'], subject='devapp Failure',
            credentials=auth, secure=secure)
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)

    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/devapp.log', maxBytes=10240,
                                       backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info('Devapp startup')

from app import routes, models, errors