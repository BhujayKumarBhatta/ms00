#!/mnt/c/mydev/microservice-tsp-billing/tokenleader/venv/bin/python

# -*- coding: utf-8 -*-

import os
import sys
import argparse


possible_topdir = os.path.normpath(os.path.join(os.path.abspath(sys.argv[0]),
                                                os.pardir,
                                                os.pardir))
                                                

# 
# if os.path.exists(os.path.join(possible_topdir,
#                                'app1',
#                                '__init__.py')):
apppath = (os.path.join(possible_topdir,
                               'tokenleader',
                               'app1'))
#    sys.path.insert(0, apppath)

sys.path.insert(0, apppath)

#print(sys.path)

from app1.authentication import admin_ops

parser = argparse.ArgumentParser()
parser.add_argument('-u', '--username', 
                  action = "store", dest = "username",
                  required = True,
                  help = "Login Name of the admin user e.g. admin",
                  default = "admin")
                  
parser.add_argument('-e', '--emailid', 
                  action = "store", dest = "emailid",
                  required = True,
                  help = "email id of the admin user",
                  default = "")                 
                  
# parser.add_argument('-r', '--role', 
#                   action = "store", dest = "role",
#                   required = True,
#                   help = "Section name in the configuration file e.g. [database] ",
#                   default = "admin")
                  
parser.add_argument('-p', '--password', 
                  action = "store", dest = "password",
                  required = True,
                  help = "password of the admin user",
                  default = "")               

try:                  
    options = parser.parse_args()    
except:
    #print usage help when no argument is provided
    parser.print_help(sys.stderr)
    sys.exit(1)

def main():
   username = options.username
   emailid = options.emailid   
   password = options.password 
   
   admin_ops.register_admin_user(username, emailid, password)
#    print (keyfilepath, confilepath, conf_section, conf_option)
#    print (options)

if __name__ == '__main__':
	main()
	
'''
/mnt/c/mydev/microservice-tsp-billing/tokenleader$ ./register_admin.sh  -u admin -e admin@itc.in -p admin
'''
	
    
