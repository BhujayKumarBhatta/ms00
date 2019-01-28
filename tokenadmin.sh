#!./venv/bin/python

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

subparsers = parser.add_subparsers(help='sub-command help')

add_parser = subparsers.add_parser('add', help='help for add command')
                  
add_parser.add_argument('-u', '--username', 
                  action = "store", dest = "username",
                  required = True,
                  help = "Login Name of the admin user e.g. admin",
                  default = "admin")
                  
add_parser.add_argument('-e', '--emailid', 
                  action = "store", dest = "emailid",
                  required = True,
                  help = "email id of the admin user",
                  default = "") 

add_parser.add_argument('-r', '--rolename', 
                  action = "store", dest = "rolename",
                  required = True,
                  help = "role name of the  user",
                  default = "") 
                  
add_parser.add_argument('-p', '--password', 
                  action = "store", dest = "password",
                  required = True,
                  help = "password of the admin user",
                  default = "")   

list_parser = subparsers.add_parser('list', help='help for list command') 

list_parser.add_argument('-a', '--all', 
                  action = "store_true", dest = "all",
                  required = False,
                  help = "list all users with admin role ",
                  default = "")  

list_parser.add_argument('-u', '--username', 
                  action = "store", dest = "username",
                  required = False,
                  help = "give the user name after username to list only one user",
                  default = "")  
          
                  
delete_parser = subparsers.add_parser('delete', help='help for delete command') 

delete_parser.add_argument('-u', '--username', 
                  action = "store", dest = "username",
                  required = True,
                  help = "list all users with admin role ",
                  default = "")  

delete_parser.add_argument('-e', '--emailid', 
                  action = "store", dest = "emailid",
                  required = True,
                  help = "email id of the admin user",
                  default = "") 
                  
##############Role Additon and Deletion #############################################################################                  
addrole_parser = subparsers.add_parser('addrole', help='help for addrole command') 

addrole_parser.add_argument('-n', '--rolename', 
                  action = "store", dest = "rolename",
                  required = False,
                  help = "name of the role e.g. admin",
                  )

listrole_parser = subparsers.add_parser('listrole', help='help for addrole command') 

listrole_parser.add_argument('-n', '--rolename', 
                  action = "store", dest = "rolename",
                  required = False,
                  help = "name of the role e.g. admin",
                  )


deleterole_parser = subparsers.add_parser('deleterole', help='help for deleterole command') 

deleterole_parser.add_argument('-n', '--rolename', 
                  action = "store", dest = "rolename",
                  required = True,
                  help = "name of the role e.g. admin",
                  )

try:                    
    options = parser.parse_args()
    #print('executing {arg} command with options {opt} :'.format(arg=sys.argv[1], opt=options))
    
except:
    #print usage help when no argument is provided
    parser.print_help(sys.stderr)
    sys.exit(1)

def main():
        
    if  (sys.argv[1] == 'add'):
        password = options.password
        username = options.username
        emailid = options.emailid
        rolename = options.rolename
        if rolename:
        	admin_ops.register_user(username, emailid, password, rolename)
        else:
        	admin_ops.register_user(username, emailid, password)
    	
    if (sys.argv[1] == 'list'):
     	if options.all:
     	    admin_ops.list_admin_users()
     	if options.username:
     		admin_ops.list_admin_users(options.username)
    
    if  (sys.argv[1] == 'delete'):        
        username = options.username
        emailid = options.emailid
        admin_ops.delete_admin_user(username, emailid)
        
    if  (sys.argv[1] == 'addrole'):        
        role_name = options.rolename        
        admin_ops.register_role(role_name)
        
    if  (sys.argv[1] == 'listrole'):        
        if  options.rolename:       
        	admin_ops.list_roles(options.rolename)
        else:
        	admin_ops.list_roles()
        
    if  (sys.argv[1] == 'deleterole'):        
        role_name = options.rolename        
        admin_ops.delete_role(role_name)
    		
    		
  
    
if __name__ == '__main__':
	main()
	
'''
/mnt/c/mydev/microservice-tsp-billing/tokenleader$ ./tokenadmin.sh  -h    to get help
'''
	
    
