# import os
import sys
from app_run import app   
from app1 import db
from app1.authentication import models
from app1.authentication.models import User

    
def register_admin_user(uname, email, pwd, role='admin'):
    with app.app_context():
        u1 = User(username=uname, email=email, role=role)
        u1.set_password(pwd)     
        try:
            db.session.add(u1)        
            db.session.commit()
            print("admin user has been  registered sucessfully")
        except  Exception as e:
            print("user  could not be registered , the erro is: \n  {}".format(e))
    
def list_admin_users(name='all'):
    with app.app_context():
        if name == 'all':
            ulist = User.query.filter_by(role='admin')
            for u in ulist:
                print(u.username, u.email)
        else:
            u = User.query.filter_by(username=name).first()
            print(u)
            print(u.username, u.email)

def delete_admin_user(uname, email, role='admin'):
    with app.app_context():
        try:        
            u1 = User.query.filter_by(username=uname).first()
        except Exception as e:
            print('user is not found in the database due to error {}'.format(e))  
        if u1:
            message = ('Are you sure to delete user :{}, {}  with id {} \n'
                         'Type \'yes\' to confirm  deleting user or no to abort:  '.format(
                             u1.username, u1.email , u1.id))
            
            uinput = input(message)
       
            if uinput == 'yes':          
                try:
                    db.session.delete(u1)        
                    db.session.commit()
                    print(" User {} has been  deleted sucessfully".format(uname))
                except  Exception as e:
                         print("user  could not be deleted , the erro is: \n  {}".format(e))
            else:
                print('\n Aborting deletion')
        else:
            print('User  not found in database')
            sys.exit(1)
            
         
                
        
                 
            
            