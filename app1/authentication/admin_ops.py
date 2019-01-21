import os
import sys



# If ../sahara/__init__.py exists, add ../ to Python search path, so that
# it will override what happens to be installed in /usr/(local/)lib/python...
# possible_topdir = os.path.normpath(os.path.join(os.path.abspath(sys.argv[0]),
#                                                 os.pardir,
#                                                 os.pardir))
# print(possible_topdir)
# 
# if os.path.exists(os.path.join(possible_topdir,
#                                'tokenleader',
#                                '')):
#     sys.path.insert(0, possible_topdir)
    
from app1 import db
from app1.authentication import models
from app1.authentication.models import User

    
def register_admin_user(uname, email, pwd, role='admin'):
    u1 = User(username=uname, email=email, role=role)
    u1.set_password(pwd)     
    try:
        db.session.add(u1)        
        db.session.commit()
        print("admin user has been  registered sucessfully")
    except:
        print("user  could not be registered ")
    

