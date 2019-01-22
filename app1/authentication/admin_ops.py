# import os
# import sys
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
    

