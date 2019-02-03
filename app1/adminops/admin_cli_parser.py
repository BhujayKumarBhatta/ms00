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

from app_run import app 
app.app_context().push()

from app1.adminops import  admin_functions as af

# parser = argparse.ArgumentParser(add_help=False)

parser = argparse.ArgumentParser(add_help=False)


subparser = parser.add_subparsers()

list_parser = subparser.add_parser('list', help='List contents' ) #parents = [parser])
list_parser.add_argument('entity', choices=['org', 'ou', 'dept', 'wfc', 'role', 'user' ])
list_parser.add_argument('-n', '--name', 
                  action = "store", dest = "name",
                  required = True,
                  help = "Name of the entitiy , type 'all' as name while listing ",
                  )
# 
# 
delete_parser = subparser.add_parser('delete', help='delete entity')
delete_parser.add_argument('entity', choices=['org', 'ou', 'dept', 'wfc', 'role', 'user' ])
delete_parser.add_argument('-n', '--name', 
                  action = "store", dest = "name",
                  required = True,
                  help = "Name of the entitiy , type 'all' as name while listing ",
                  )


add_parser = subparser.add_parser('add', help='List contents')
add_parser.add_argument('entity', choices=['org', 'ou', 'dept', 'role' ])
add_parser.add_argument('-n', '--name', 
                  action = "store", dest = "name",
                  required = True,
                  help = "Name of the entitiy , type 'all' as name while listing ",
                  )
add_parser.add_argument('--orgtype' , action = "store", dest = "orgtype",
                  required = False,
                  help = "internal or external org , to be used while registtering org ",
                  default = "internal")
add_parser.add_argument('--wfcname' , action = "store", dest = "wfcname",
                  required = False,
                  help = "wfc name linked with the role , to be used while registtering role ",
                  )


addwfc_parser = subparser.add_parser('addwfc', help='add a wfc , work function context ')
addwfc_parser.add_argument('-n', '--name', 
                  action = "store", dest = "name",
                  required = True,
                  help = "Name of the wfc simple string ,",
                  )
addwfc_parser.add_argument('--wfcorg' , action = "store", dest = "wfcorg",
                  required = True,
                  help = "org  name linked with the wfc , to be used while registtering wfc ",
                  ) 
addwfc_parser.add_argument('--wfcou' , action = "store", dest = "wfcou",
                  required = True,
                  help = "org  unit name linked with the wfc , to be used while registtering wfc ",
                  ) 
addwfc_parser.add_argument('--wfcdept' , action = "store", dest = "wfcdept",
                  required = True,
                  help = "dept name linked with the wfc , to be used while registtering wfc ",
                  ) 


adduser_parser = subparser.add_parser('adduser', help='List contents')
adduser_parser.add_argument('-n', '--name', 
                  action = "store", dest = "name",
                  required = True,
                  help = "Name of the user",
                  )
adduser_parser.add_argument('--password' , action = "store", dest = "password",
                  required = True,
                  help = "password for the user ",
                  )
adduser_parser.add_argument('--emailid' , action = "store", dest = "emailid",
                  required = True,
                  help = "email id of  the user ",
                  )
adduser_parser.add_argument('--rolenames' , action = "store", dest = "rolenames",
                  required = True,
                  help = "comma separed names of roles which were already registered in the role db.\
                   there should not be any space beteween the role names. \
                   examaple  , --rolenames role1,role2,role3 " 
                  )  

try:                    
    options = parser.parse_args()  
except:
    #print usage help when no argument is provided
    parser.print_help(sys.stderr)    
    sys.exit(1)

def main():
    if len(sys.argv)==1:
        # display help message when no args are passed.
        parser.print_help()
        sys.exit(1)
    
    #print(sys.argv[3])
    entity_name = options.name
    
    if  sys.argv[1] == 'add':
        
        if options.entity == 'org':      
            af.register_org(entity_name)
                
        
        if options.entity == 'ou':      
            af.register_ou(entity_name)
                
                
        if options.entity == 'dept':      
            af.register_dept(entity_name)
          
                
        if options.entity == 'role':
            af.register_role(entity_name, options.wfcname)
            
    if  sys.argv[1] == 'addwfc':
        af.register_work_func_context(entity_name, options.wfcorg, options.wfcou, options.wfcdept)
                
    if  sys.argv[1] == 'adduser':        
        password = options.password
        username = options.name
        emailid = options.emailid
        rolenames = options.rolenames
        if rolenames:
            role_list = []
            if  not ',' in rolenames:
                role_list.append(rolenames)
            else:
                role_list = rolenames.split(',')
            af.register_user(username, emailid, password, role_list)
        else:
            af.register_user(username, emailid, password) 
        #af.delete_user(entity_name, options.email, options.password, options.roles)      
    
    if  sys.argv[1] == 'list':
        
        if options.entity == 'org':      
            if entity_name == 'all':
                af.list_org()
            else:
                af.list_org(entity_name)
                
        
        if options.entity == 'ou':      
            if entity_name == 'all':
                af.list_ou()
            else:
                af.list_ou(entity_name)
                
                
        if options.entity == 'dept':      
            if entity_name == 'all':
                af.list_dept()
            else:
                af.list_dept(entity_name)
                
        
        if options.entity == 'wfc':      
            if entity_name == 'all':
                af.list_wfc()
            else:
                af.list_wfc(entity_name)
                
                
        if options.entity == 'role':      
            if entity_name == 'all':
                af.list_role()
            else:
                af.list_role(entity_name)
                
                
        if options.entity == 'user':      
            if entity_name == 'all':
                af.list_users()
            else:
                af.list_users(entity_name)         
        
    
    if  sys.argv[1] == 'delete': 
        
        
        if options.entity == 'org':      
            af.delete_org(entity_name)
                
        
        if options.entity == 'ou':      
            af.delete_ou(entity_name)
                
                
        if options.entity == 'dept':      
            af.delete_dept(entity_name)
                
        
        if options.entity == 'wfc':      
            af.delete_wfc(entity_name)
                
                
        if options.entity == 'role':      
            af.delete_role(entity_name)
                
                
        if options.entity == 'user':      
            af.delete_user(entity_name)           
            
    
if __name__ == '__main__':
    main()
    
'''
/mnt/c/mydev/microservice-tsp-billing/tokenleader$ ./tokenadmin.sh  -h    to get help
'''
    
    
