from flask import  current_app
from werkzeug.security import generate_password_hash, check_password_hash

from app1 import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    
    def __repr__(self):
        return '<User {}>'.format(self.username)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return  check_password_hash(self.password_hash, password)
        
    def to_dict(self):
        data = {
            'id': self.id,
            'username': self.username,
            'email':  self.email,            
            }
        return data
    
    
    
'''

from app_run import app
app.app_context().push()
from app1 import db
from app1.authentication.models import User
u1 = User(username='susan', email='susan@abc.com')
db.session.add(u1)
db.session.commit()


from app_run import app
app.app_context().push()
from app1 import db
from app1.authentication.models import User
u1 = User.query.filter_by(username='susan').first()
u1.set_password('mysecret')
u1.check_password('mysecret')
db.session.commit()

from app_run import app
app.app_context().push()
from app1 import db
from app1.authentication.models import User
u1 = User.query.filter_by(username='susan').first()
u1.check_password('mysecret')

'''
