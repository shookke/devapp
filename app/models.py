from app import db, login
from flask_login import UserMixin
from flask_security import UserMixin, RoleMixin
from werkzeug.security import generate_password_hash, check_password_hash
from hashlib import md5
from datetime import datetime

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

# Define models
roles_users = db.Table('roles_users',
        db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
        db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))

class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password = db.Column(db.String(128))
    token = db.Column(db.String(128))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<User {}>'.format(self.username) 
    '''
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    '''
    def check_token(self, token):
        token = User.query.filter_by(token).first()
        if token is not None:
            return False

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

class Container(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)
    database = db.Column(db.String(64), index=True, unique=True)
    db_user = db.Column(db.String(64), index=True, unique=True)
    db_pw = db.Column(db.String(128))
    prefix = db.Column(db.String(32), index=True, default="wp_")
    port = db.Column(db.String(32), index=True, unique=True)
    url = db.Column(db.String(120), index=True)
    status = db.Column(db.String(32), index=True)

    def is_active(self, name):
        if self.status == 'SUCCESS':
            return True
        else:
            return False


    def __repr__(self):
        return '<Container {}>'.format(self.name, self.status)