What it does 
===================================================================
tokenleader has two simple operations:
1) recieves users request ,  autehnticate his and provides a  token  which carries  more users informations such as 
	a) user's roles ( one user can have multiple roles, although most of the cases one will suffice)  
	b) role  is mapped with  a wfc ( work function context)   
	c) wfc is a combination of  organization name, organization unit name and departname 

A typical token request call is :   
curl -X POST -d '{"username": "admin", "password": "admin"}'  \
-H "Content-Type: Application/json"  localhost:5001/token/gettoken

The validity period of the token can be set through the settings.ini in future , currently it is fixed as one hour.

2) receives a token from user , can validate and unencrypt the users information. 

token can be used for authenticating an user wiithout the need for user
To verify token:  
 curl -H  "X-Auth-Token:<paste toekn here>"  localhost:5001/token/verify_token  
 
 Why token service and how it works
 ======================================================================================
 in situtaions where a service or a client need to make several  http /REST call to an 
 application/service(microservice)/server or  to multiple applications/services/servers, 
 sending the user name and password repeatedly over the http traffic is not desiarable, neither it is good
 to store the user name and password in servers session for a stateless application. In thses cases token based 
 authentication helps.
 
 Once an user or service obtain a token, subsequent calls to the server or even to different servers can be made
 using the token instead of username and password. The server then will make a validation call to tokenleader for 
 authentication and also will retrieve role name and wfc information. 
 
 
 The information retrieved  from the token leader then can be used by the server for granting proper authorization to the 
 server resources . Therefore authentication is handled  by the tokenleader application whereas the authorization is handled 
 by the applicaion being served to the user. 
 
 each application uses a local role to acl map. For each api route there is one acl name which either deny or permits the 
 http call to the  api route . further  to control how much data to be given access to the user , the wfc details  will be 
 used for filtering  the data query ( mainly data persistance and query)

Please follow the installation and configuration steps  
======================================================================================
git config --global http.sslVerify false ( in case of server ssl cert verification error)  

git clone <your project>      

e.g.   git clone  git@github.com:microservice-tsp-billing/tokenleader.git  

cd tokenleader    

virtualenv -p python3 venv  

source venv/bin/activate  

pip install --upgrade pip  

pip install -r requirement.txt ( pycrypto failed)    

ssh-keygen < press enter to select all defaults>    

python -m unittest discover tests    

to run single unit test  
python -m unittest tests.unittests.test_admin_ops.TestAdminOps.test_abort_delete_admin_user_input_not_yes  

for token generation and verification  testing this is a useful test  
python -m unittest tests.test_auth.TestToken.test_token_gen_n_verify_success_for_registered_user_with_role   


TO set up the tokenleqder the following entities need to be registered in sequence   
from the root directory of  tokenleader  
====================================================================================
./adminops.sh  -h  provides help to understand the various options of admin funciton os tokenleader  

./adminops.sh   add  org   -n org1  
./adminops.sh   add  ou   -n ou2  
./adminops.sh   add  dept   -n  dept1  
 ./adminops.sh   addwfc -n wfc1 --wfcorg org1 --wfcou ou1 --wfcdept dept1 
 ./adminops.sh   list  wfc  -n wfc2  
 #3 wfc2 <WorkFunctionContext wfc2 <Organization org1> <OrgUnit ou1> <Department dept1> >  
  
 ./adminops.sh   add  role  -n role1 --wfcname wfc1   
 
 check that the wfc has been assigned correctly   
 ./adminops.sh   list  role  -n role1  
id: 1,  name: role1 , wfc: wfc1 , wfcorg: org1, wfcou: ou1, wfcdept: dept1    
 
 ./adminops.sh adduser -n user10 --password user10 --emailid user10 --rolenames role10  
 
 ./adminops.sh   list  wfc  -n all
 ./adminops.sh   list  dept  -n all   or  ./adminops.sh   list  dept  -n dept1 
 
 ./adminops.sh delete user -n user10
 
 
 To check the database objects from shell, and to see  that the relational properties are working properly   
 use the follwoing :  
 ==================================================
 /microservice-tsp-billing/tokenleader$ flask shell    
from app1.authentication import models  
from app1.authentication.models import User, Role, Workfunctioncontext, Organization, OrgUnit, Department  
r1 = Role.query.filter_by('role1').first()  
r1 = Role.query.filter_by(rolename='role1').first()  
r1 
#<Role role1>  
r1.functional_context  
#<WorkFunctionContext wfc1>  
r1.functional_context.org  
#<Organization org1>  
r1.functional_context.org.name  
#'org1'  
r1.functional_context.orgunit  
#<OrgUnit ou1>  
r1.functional_context.orgunit.name  
#'ou1'  
r1.functional_context.department.name  
#'dept1'  

 



export FLASK_APP='app_run.py'  

flask run -p 5001  

ensure  the port  of the server is open from security group  


To generate token :  

curl -X POST -d '{"username": "admin", "password": "admin"}'  \
-H "Content-Type: Application/json"  localhost:5001/token/gettoken

To verify token:  
 curl -H  "X-Auth-Token:<paste toekn here>"  localhost:5001/token/verify_token  


for db migration   

flask db init   
flask db migrate -m < COMMENT >  
flask db upgrde   

if there is a change in db structure, and a migration is done , commit and push the migration directory to the git  
from the  machine where migration was done.  

For  development machine with sqllite db , there are chalenges in migration due to lil8mitiaton of database
alter capabilities inherent to sqllite. So sometimes , delelting the migration folder and and  recreating a   
fresh migartion helped.

to test the db operation  :  

(venv) bhujay@DESKTOP-DTA1VEB:/mnt/c/mydev/microservice-tsp-billing/tokenleader$ flask shell

from app1 import db  
from app1.authentication.models import User, Role  
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



Todo:


role and wfc shd not have any relation
user can have only one wfc 

===================================
User model to_dict , roles: to return role_sql_obj instead of role.name ===> 
 'roles': [role.rolename for role in self.roles]  to be changed to    'roles': [role for role in self.roles]
----------------------------------------------------------------------------------

testing to be done/changes to  get the role obj from the  roles list instead of role name as string
----------------------------------------------------------------------------------------------------
micros1 authclient ==> extract_roles_from_verified_token_n_compare_acl_map ==>
for user_role_in_token in roles_in_token:
        #for role_sql_obj in roles_in_token:
            #user_role_in_token = role_sql_obj.rolename
#             work_context_dict = {'wfcname': role.functional_context.name,
#                                  'org': role.functional_context.org.name,
#                                  'ou': role.functional_context.orgunit.name,
#                                  'dept':  role.functional_context.department.name
#                                  }
---------------------------------------------------------------------------------------------------------
tesing to be done/changes to that affect

workcontext to be instantiated as a class 

workcontext to be made avilable to  api route function when required





