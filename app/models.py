from app import db, login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from hashlib import md5
from datetime import datetime

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    token = db.Column(db.String(128))
    admin = db.Column(db.Boolean, unique=False, default=False)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<User {}>'.format(self.username) 

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

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