from flask import  current_app
from werkzeug.security import generate_password_hash, check_password_hash

from app1 import db

roles_n_user_map = db.Table('roles_n_user_map',
    db.Column('role_id', db.Integer, db.ForeignKey('role.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)    
    password_hash = db.Column(db.String(128))
    roles = db.relationship('Role', secondary=roles_n_user_map, lazy='dynamic' ,
        backref=db.backref('users', lazy='dynamic' ))
    

    
#     roles = db.relationship('Role', lazy='dynamic' ,
#         backref=db.backref('users', lazy='dynamic' ))
    
    def __repr__(self):
        return '<User {}>'.format(self.username)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
     
    def check_password(self, password):
        return  check_password_hash(self.password_hash, password)
    #Todo: need changes as well
    def is_admin(self):
        if self.role == 'admin' or self.role=='Admin' or self.role=='ADMIN':
            return True
        
    
    def to_dict(self):
        data = {
            'id': self.id,
            'username': self.username,
            'email':  self.email,
            'roles': [role.rolename for role in self.roles]
            }
        return data    
    
    
class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rolename = db.Column(db.String(64), index=True, unique=True)
    functional_context = db.relationship('Workfunctioncontext', backref = 'role', uselist=False, lazy = True)

    def __repr__(self):
        return '<Role {}>'.format(self.rolename)
    
    
class Workfunctioncontext(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True, nullable=False)
    org = db.relationship('Organization', backref = 'org', uselist=False, lazy = True)
    orgunit = db.relationship('OrgUnit', backref = 'orgunit', uselist=False, lazy = True)
    department = db.relationship('Department', backref = 'department', uselist=False, lazy = True)
    roleid = db.Column(db.Integer, db.ForeignKey('role.id'))
    
    def __repr__(self):
        return '<WorkFunctionContext {} {} {} {} >'.format(self.name,
                                                           self.org,
                                                           self.orgunit,
                                                           self.department)
    

class Organization(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True, nullable=False)
    orgtype = db.Column(db.String(64))
    auth_backend = db.Column(db.String(64))
    work_func_id = db.Column(db.Integer, db.ForeignKey('workfunctioncontext.id'))
    
    def __repr__(self):
        return '<Organization {}>'.format(self.name)
    

class OrgUnit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True, nullable=False)
    work_func_id = db.Column(db.Integer, db.ForeignKey('workfunctioncontext.id'))
    
    def __repr__(self):
        return '<OrgUnit {}>'.format(self.name)
    

class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True, nullable=False)
    work_func_id = db.Column(db.Integer, db.ForeignKey('workfunctioncontext.id'))
    
    def __repr__(self):
        return '<Department {}>'.format(self.name)
    
    

    



'''
(venv) bhujay@DESKTOP-DTA1VEB:/mnt/c/mydev/microservice-tsp-billing/tokenleader$ flask shell

from app1 import db
from app1.authentication.models import User, Role, Workfunctioncontext, Organization, OrgUnit, Department
r1 = Role(rolename='role1')
db.session.add(r1)
db.session.commit()

u = User(username='john', email='john@example.com')
db.session.add(u)
db.session.commit()
u = User.query.filter_by(username='john').first()
u
#<User john>
u.roles
#<sqlalchemy.orm.dynamic.AppenderBaseQuery object at 0x7fb94faa2e48>
u.roles=[r1]
db.session.commit()
u.roles
#<sqlalchemy.orm.dynamic.AppenderBaseQuery object at 0x7fb94fa8bf98>
for l in u.roles:
    print(l.rolename)

#role1

#======================Older code while role was not there================================================================


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
