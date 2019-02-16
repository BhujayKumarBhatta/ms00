#!./venv/bin/python

# -*- coding: utf-8 -*-

import os
import sys
import argparse
import subprocess


possible_topdir = os.path.normpath(os.path.join(os.path.abspath(sys.argv[0]),
                                                os.pardir,
                                                os.pardir))
                                                

# 
# if os.path.exists(os.path.join(possible_topdir,
#                                'app1',
#                                '__init__.py')):
apppath = (os.path.join(possible_topdir,
                               'tokenleader',
                               'tokenleader'))
#    sys.path.insert(0, apppath)

sys.path.insert(0, apppath)

#migration_dir = os.path.dirname(__file__)+'/../../migrations'
migration_path = os.path.join(os.path.dirname(__file__),
                               os.pardir , os.pardir, 'migrations')

#print(sys.path)

from tokenleader.app_run import app 
app.app_context().push()

from tokenleader.app1.adminops import  admin_functions as af
from tokenleader.app1.catalog import  catalog_functions as cf

# parser = argparse.ArgumentParser(add_help=False)

parser = argparse.ArgumentParser(add_help=False)


subparser = parser.add_subparsers()

initdb_parser = subparser.add_parser('initdb', help='initialize database' ) #parents = [parser])

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
adduser_parser.add_argument('--wfc' , action = "store", dest = "wfc",
                  required = True,
                  help = "wfc or work function context name " 
                  ) 


addservice_parser = subparser.add_parser('addservice', help='add a service in the service catalog')
addservice_parser.add_argument('-n', '--name', 
                  action = "store", dest = "name",
                  required = True,
                  help = "Name of the microservice",
                  )
addservice_parser.add_argument('--password' , action = "store", dest = "password",
                  required = True,
                  help = "service account name password, this password will \
                  be used for intra service communication",
                  ) 
addservice_parser.add_argument('--urlext' , action = "store", dest = "urlext",
                  required = False,
                  help = "url of the service endpoint , that is avilable to all users ",
                  ) 
addservice_parser.add_argument('--urlint' , action = "store", dest = "urlint",
                  required = True,
                  help = "url of the service endpoint , that is used for service to service \
                  communication and is not avilable to all users. This is useful when service network and \
                  user network is different",
                  )
addservice_parser.add_argument('--urladmin' , action = "store", dest = "urladmin",
                  required = False,
                  help = "url of the service endpoint , that is used for admin activities. \
                  This is useful to segregte the admin network from user and service network",
                  ) 


deletservice_parser = subparser.add_parser('deletservice', help='delete a service from service catalog')
deletservice_parser.add_argument('-n', '--name', 
                  action = "store", dest = "name",
                  required = True,
                  help = "Name of the microservice",
                  )

listservice_parser = subparser.add_parser('listservice', help='List a service from service catalog')
listservice_parser.add_argument('-n', '--name', 
                  action = "store", dest = "name",
                  required = True,
                  help = "Name of the microservice",
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
        
    if sys.argv[1] == 'initdb':
        print("performing db table creation as per the last schema"
              " change in migration dir : {}".format(migration_path))
        subprocess.run(["flask" , "db" , "upgrade", "-d",  migration_path, ])
    
    #print(sys.argv[3])
#     entity_name = options.name
    
    if  sys.argv[1] == 'add':
        
        if options.entity == 'org':      
            af.register_org(options.name)
                
        
        if options.entity == 'ou':      
            af.register_ou(options.name)
                
                
        if options.entity == 'dept':      
            af.register_dept(options.name)
          
                
        if options.entity == 'role':
            af.register_role(options.name)
            
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
            af.register_user(username, email=emailid, pwd=password, wfc_name=options.wfc, roles=role_list,)
        else:
            af.register_user(username, email=emailid, pwd=password, wfc_name=options.wfc) 
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
         
    if  sys.argv[1] == 'addservice':
        cf.add_service(options.name, options.password, options.urlext, options.urlint, options.urladmin)
        
        
    if  sys.argv[1] == 'listservice': 
        if options.name == 'all':
            cf.list_services()
        else:
            cf.list_services(options.name)
          
    
    if  sys.argv[1] == 'deletservice': 
        cf.delete_service(options.name)           
    
if __name__ == '__main__':
    main()
    
'''
/mnt/c/mydev/microservice-tsp-billing/tokenleader$ ./tokenadmin.sh  -h    to get help
'''
    
    
