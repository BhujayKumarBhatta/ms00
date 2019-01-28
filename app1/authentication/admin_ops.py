# import os
import sys
from app_run import app   
from app1 import db
from sqlalchemy import exc
from app1.authentication import models
from app1.authentication.models import User, Role


def register_role(rname):
    with app.app_context():
        r1 = Role(rolename=rname)            
        try:
            db.session.add(r1)        
            db.session.commit()
            msg = ("role: {} has been  registered sucessfully".format(rname))
        except exc.IntegrityError:
            msg = ('databse integrity error, role by the same name may be already present')
        except  Exception as e:
            msg =("role: {} could not be registered , the erro is: \n  {}".format(rname, e))
            
        print(msg)    
        return msg

def list_roles(rname=None):
    with app.app_context():               
        if not rname :
            rlist = Role.query.all()            
            for r in rlist:
                #print(r)
                if r:    
                    print("role id: {}, role name: {}".format(r.id, r.rolename))
            return rlist
        else:
            r = Role.query.filter_by(rolename=rname).first()
            #print(r)
            if r:
                print("role id: {}, role name: {}".format(r.id, r.rolename))
            return r
            
def delete_role(rname):
    with app.app_context():
        try:        
            r1 = Role.query.filter_by(rolename=rname).first()
        except Exception as e:
            status = 'Role: {} is not found in the database due to error {}'.format(rname, e)
            print(status)  
        if r1:
            message = ('Are you sure to delete role :{}  with id {} \n'
                         'Type \'yes\' to confirm  deleting user or no to abort:  '.format(
                             r1.rolename, r1.id))
            
            uinput = get_input(message)
       
            if uinput == 'yes':          
                try:
                    db.session.delete(r1)        
                    db.session.commit()
                    status = "Role:  {} has been  deleted successfully".format(rname) 
                    print(status)
                except  Exception as e:
                        status = "Role: {} could not be deleted , the erro is: \n  {}".format(rname, e)
                        print(status)
            else:
                status = 'Aborting deletion'
                print(status)
        else:
            status = 'Role  not found in database'
            print(status)
            
            
        return status    
    
    
def get_validated_roles(roles):
    '''
    param roles: comma separeted text for role name within  a list
    type: list
    
    '''
    valid_role_list =[]
    invalid_role_list = []
    
    for role in roles:        
        r = Role.query.filter_by(rolename=role).first()        
        if r:
            valid_role_list.append(r)            
        else:            
    
            invalid_role_list.append(role)
    if  invalid_role_list:        
        msg = ("following roles: {} does not exist, create it first".format(invalid_role_list))
        print(msg)    
    if valid_role_list:
        return valid_role_list
    
def register_user(uname, email, pwd, roles=None):
    with app.app_context():
        if roles:
            valid_role_objects = get_validated_roles(roles)
            u1 = User(username=uname, email=email, roles=valid_role_objects)
        else:            
            u1 = User(username=uname, email=email)
        u1.set_password(pwd)     
        try:
            db.session.add(u1)        
            db.session.commit()
            msg = ("user has been  registered sucessfully")
        except exc.IntegrityError:
            msg = ('databse integrity error, username or email address is already present')
        except  Exception as e:
            msg ("user  could not be registered , the erro is: \n  {}".format(e))
        
        print(msg)
        return msg
    
def list_admin_users(name=None):
    with app.app_context():               
        if not name :
            ulist = User.query.all()
            #ulist = User.query.all()
            for u in ulist:
                #print(u)
                if u:    
                    print(u.username, u.email, ','.join([r.rolename for r in u.roles]) )
#                     for r in u.roles:
#                         print(r.rolename)
            return ulist
        else:
            u = User.query.filter_by(username=name).first()
            #print(u)
            if u:
                 print(u.username, u.email, ','.join([r.rolename for r in u.roles]) )
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
         
                
        
                 
            
            