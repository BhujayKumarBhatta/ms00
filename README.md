What it does 
===================================================================
tokenleader has three  simple operations:
1) recieves users request ,  autehnticates her and provides a  token  which carries  more users informations such as 
	a) user's roles ( one user can have multiple roles, although most of the cases one will suffice)  
	b) user is  alos mapped with  a wfc ( work function context)   
	c) wfc is a combination of  organization name, organization unit name and departname 

A typical token request call is :   
curl -X POST -d '{"username": "admin", "password": "admin"}'  \
-H "Content-Type: Application/json"  localhost:5001/token/gettoken

The validity period of the token can be set through the settings.ini in future , currently it is fixed as one hour.

2) receives a token from user , can validate and unencrypt the users information. 

3) maintains a catalog for all the microservies . The entry for services , it includes service name ,
   servie account password ( we have to see if this is required at all) , url for the service endpoint.
   A client can query tokenleader by service name and will thus get the url for the service .
   
   For each service end point three url can be registered , one for internal , this is  the default url .
   External url , when you want to segregate the users network from service network 
   and another is admin network , which can be further separated from the above two network
   

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
 
 
 For the developer
 ==============================================================================================
 For authorization , there is a enforcer decorator to be used by each microservice .  
 A sample microsdervice with this decoraator has been shown in  micros1 repo . Any api route which is bind 
 with this decorator will retrieve role and wfc from the tokenleader service.   
 The role will be used by the decorator to compare with the local acl map yml file for allowing or denying the  
 access to api route url. 
 The wfc will be passed to the api route function for later usage by the function for database query filtering. 
 The api route function must have a keyword argument 'wfc'  for the enforcer decorator to work. 
 
 Example :
    @bp1.route('/test1', methods=[ 'POST'])
	@authclient.enforce_access_rule_with_token('service1:first_api:rulename1', 
	                                           role_acl_map_file, sample_token)
	def acl_enforcer_func_for_test(wfc=None):
	    msg = ("enforcer decorator working ok with wfc org = {},"
	            "orgunit={}, dept={}".format(wfc.org, wfc.orgunit, wfc.department))
	  
	    return msg
	  
In the above example, the decorator  impose aceess control on the route /test1 . 

role name for the user  is retrived from the token leader , compared with the rule to acl map yml file 
(role_acl_map_file) which is maintained locally in the server where the service is running .

decorator alos retrived work function context for the  user from tokenleader and passed it to 
original route function acl_enforcer_func_for_test .   The route function mandatorily to have a 
parameter called wfc as argument for the wfc , to get the value from the decorator.

now within the acl_enforcer_func_for_test  funtion  , wfc attributes like org, orgunit and department is used
to display a message. They actually  to be used for database query filtering so that based on the work function
user is able to view only relevant information.


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
  
 ./adminops.sh   add  role  -n role1   
  
 ./adminops.sh adduser -n user10 --password user10 --emailid user10 --rolenames role10  --wfc wfc1
 
 ./adminops.sh   list  user  -n all  or   ./adminops.sh   list  user  -n user1
 
 ./adminops.sh   list  dept  -n all   or  ./adminops.sh   list  dept  -n dept1 
 
 ./adminops.sh delete user -n user10  for deleting the user 
 
 
  ./adminops.sh  addservice  -n tokenleader --password tokenleader --urlint localhost:5001


./adminops.sh listservice -n all
#{'name': 'micros1', 'endpoint_url_internal': None, 'id': 1, 'endpoint_url_external': 'localhost:5002', 'endpoint_url_admin': None}

 ./adminops.sh deletservice -n servie1
 
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


export FLASK_APP='app_run.py'  

flask run -p 5001  

ensure  the port  of the server is open from security group  


To generate token :  
===================================================
curl -X POST -d '{"username": "admin", "password": "admin"}'  \
-H "Content-Type: Application/json"  localhost:5001/token/gettoken

what you get from tokenleader:
========================================
{'message': 'success', 'status': 'success', 'auth_token': 'eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE1NDkzNzg3MDgsImV4cCI6MTU0OTM4MjMwOCwic3ViIjp7IndmYyI6eyJpZCI6MSwibmFtZSI6IndmYzEiLCJkZXBhcnRtZW50IjoiZGVwdDEiLCJvcmciOiJvcmcxIiwib3JndW5pdCI6Im91MSJ9LCJpZCI6MSwidXNlcm5hbWUiOiJ1MSIsInJvbGVzIjpbInJvbGUxIl0sImVtYWlsIjoidTFAYWJjLmNvbSJ9fQ.I2VL1bND5IPynnjGjqOm18IeQsVDJItP9OObPU6817BqTTfk9uTe825fbOX5Zz1-SRm6yKxOOHYzwCUwt7UC1DNyrepV6UlN14RI990xLrfwX1cGAGT7ppW8rTUZks8d5NdcE9DjMfilUwN2dJ15YxsBHgsjYvuV8jBPR-y1gV7ArBcnE2ejY7pVMAxnzzBQz4OtmKARErdYd7BsE6wTqYCdoDV-T_M1ZUe_0u4kJ5vgkxyoWumCHXkt8-S75dxMrq8BePrLd3W-Y9kQjGpmEFX9Xr55oTqexlCtJ9i8920Lh3tyDDb79IPbzSt516PBrjaql98eL1ijuM83IXQhuA'}



To verify token:  
================================================
 curl -H  "X-Auth-Token:<paste toekn here>"  localhost:5001/token/verify_token  

How the verified toekn data looks like :
===========================================================================
{
  "message": "Token has been successfully decrypted",
  "payload": {
    "exp": 1549382308,
    "iat": 1549378708,
    "sub": {
      "email": "u1@abc.com",
      "id": 1,
      "roles": [
        "role1"
      ],
      "username": "u1",
      "wfc": {
        "department": "dept1",
        "id": 1,
        "name": "wfc1",
        "org": "org1",
        "orgunit": "ou1"
      }
    }
  },
  "status": "Verification Successful"
}



for initial setup or when db model is changed
===================================================================
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
========================================================================================
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


1)operation scope filtering based on users org, div, dept details 
Todo:
role and wfc shd not have any relation - done
user can have only one wfc  - done 
user to dict now gives wfc dictionary as well

tesing to be done/changes to that affect  - upto verification unit test is passed 


workcontext to be instantiated as a class 

workcontext to be made avilable to  api route function when required

ext  important works:
 
2) centralized catalogue for all microservice endpoints and 
3) client for tokenleader



