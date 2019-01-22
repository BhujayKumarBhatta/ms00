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
            return ulist
        else:
            u = User.query.filter_by(username=name).first()
            print(u)
            print(u.username, u.email)
            return u

def get_input(text):
    return input(text)

def delete_admin_user(uname, email, role='admin'):
    with app.app_context():
        try:        
            u1 = User.query.filter_by(username=uname).first()
        except Exception as e:
            status = 'user is not found in the database due to error {}'.format(e)
            print(status)  
        if u1:
            message = ('Are you sure to delete user :{}, {}  with id {} \n'
                         'Type \'yes\' to confirm  deleting user or no to abort:  '.format(
                             u1.username, u1.email , u1.id))
            
            uinput = get_input(message)
       
            if uinput == 'yes':          
                try:
                    db.session.delete(u1)        
                    db.session.commit()
                    status = " User {} has been  deleted sucessfully".format(uname) 
                    print(status)
                except  Exception as e:
                        status = "user  could not be deleted , the erro is: \n  {}".format(e)
                        print(status)
            else:
                status = 'Aborting deletion'
                print(status)
        else:
            status = 'User  not found in database'
            print(status)
            
            
        return status    
         
                
        
                 
            
            