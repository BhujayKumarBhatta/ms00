from flask import  current_app
from werkzeug.security import generate_password_hash, check_password_hash

from tokenleader.app1 import db
import this



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
    

class Workfunctioncontext(db.Model):
    '''relationship from wfc to  Organization, OrgUnit and Department are 'Many to One' type
       whereas  User to Workfunctioncontext is 'Many to one' and
        Workfunctioncontext to User is one to many, i,e, wfc.users  which is created 
        Users class side'''
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True, nullable=False)
    org = db.relationship('Organization', backref = 'org', uselist=False, lazy = True)
    orgunit = db.relationship('OrgUnit', backref = 'orgunit', uselist=False, lazy = True)
    department = db.relationship('Department', backref = 'department', uselist=False,lazy = True)
##################################################################################################
# the follwinf line is no more required as User class is providing  a 'users'  backref to Workfunctioncontext
#     users = db.relationship('User', backref='wfc', lazy=True)
# as a result we get 
# >>> w.users
# >>>[<User user1>, <User user2>]
################################################################################################
    
    def __repr__(self):
        return '<WorkFunctionContext {} {} {} {} >'.format(self.name,
                                                           self.org,
                                                           self.orgunit,
                                                           self.department)
    def to_dict(self):
        data = {
            'id': self.id,
            'name': self.name,
            'org':  self.org.name,
            'orgunit':  self.orgunit.name,
            'department':  self.department.name            
            }
        return data


class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rolename = db.Column(db.String(64), index=True, unique=True, nullable=False)
    userid = db.Column(db.Integer, db.ForeignKey('user.id'))
#     functional_context = db.relationship('Workfunctioncontext', backref = 'role', uselist=False, lazy = True)

    def __repr__(self):
        return '<Role {}>'.format(self.rolename)    
    

#This mapper table is used for many to many relationship between user and role
roles_n_user_map = db.Table('roles_n_user_map',
    db.Column('role_id', db.Integer, db.ForeignKey('role.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)


class User(db.Model):
    '''
    ######################################################################################
# the following line is for one to one relationship and was moving the relationship 
# pointer to  one wfc as we create users with same wfc .e.g user1 -->wfc1 , when user2--wfc2
# will be created user1 to wfc1 will be deleted
#     wfc = db.relationship('Workfunctioncontext', backref = 'user', uselist=False, ) #lazy = True

# We need to use many to one realtionship instead as given below.  by giving backref , 
#Workfunctioncontext will have the Workfunctioncontext.users avilable
#no need for creating users relationship st the Workfunctioncontext class end

# moreover , while user  exists with a wfc assigned to it , the wfc can not be deleted . the error will be
# wfc1 could not be deleted , the erro is:
# (sqlite3.IntegrityError) NOT NULL constraint failed: 
# user.wfc_id [SQL: 'UPDATE user SET wfc_id=? WHERE user.id = ?'] 
# [parameters: ((None, 1), (None, 2))] (Background on this error at: http://sqlalche.me/e/gkpj)
#################################################################################################
'''
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    email = db.Column(db.String(120), index=True, unique=True)    
    password_hash = db.Column(db.String(128))
#     roles = db.relationship('Role', secondary=roles_n_user_map, lazy='dynamic' ,
#         backref=db.backref('users', lazy='dynamic' ))
    roles = db.relationship('Role', secondary=roles_n_user_map, 
        backref=db.backref('users' ))

    wfc_id = db.Column(db.Integer, db.ForeignKey('workfunctioncontext.id'), nullable=False)
    wfc = db.relationship("Workfunctioncontext", backref="users")    
    
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
            'roles': [role.rolename for role in self.roles],
            #'roles': [role for role in self.roles] flsk is not able to return sql object , expecting string
            'wfc': self.wfc.to_dict()
            }
        return data    
################################################################################################ The user object listing will be like this

# [{'username': 'user1', 'wfc': {'name': 'wfc1', 'orgunit': 'ou1', 'department': 'dept1', 'id': 1, 'org': 'org1'}, 'roles': ['role1'], 'id': 1, 'email': 'user1'}, 
# {'username': 'user2', 'wfc': {'name': 'wfc1', 'orgunit': 'ou1', 'department': 'dept1', 'id': 1, 'org': 'org1'}, 'roles': ['role1'], 'id': 2, 'email': 'user2'}]    
#     



    

    



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


from tokenleader.app_run import app
app.app_context().push()
from tokenleader.app1 import db
from tokenleader.app1.authentication.models import User, Role, Workfunctioncontext, Organization, OrgUnit, Department
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


>>> data = { 'roles': [ {'rolename': role.rolename, 'wfcname': role.functional_context.name, 'org': role.functional_context.org,}  for role in roles] }
>>> data

{'roles': [{'org': <Organization org10>, 'rolename': 'role10', 'wfcname': 'wfc10'}]}
>>> data = { 'roles': [ {'rolename': role.rolename, 'wfcname': role.functional_context.name, 'org': role.functional_context.org.name,}  for role in roles] }
>>> data
{'roles': [{'org': 'org10', 'rolename': 'role10', 'wfcname': 'wfc10'}]}
>>>
==========================================================================
rm /tmp/auth.db
./adminops.sh initdb
./adminops.sh add org -n org1
./adminops.sh add ou -n ou1
./adminops.sh add dept -n dept1
./adminops.sh addwfc -n wfc1 --wfcorg org1 --wfcou ou1 --wfcdept dept1
./adminops.sh add role -n role1
./adminops.sh adduser -n user1 --password user1 --emailid user1 --rolenames role1  --wfc wfc1







'''
