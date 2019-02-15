change log 
============

ver 0.6
--------------
1. check  presence of required parameters in /etc/token/leader/tokenleader_settings.ini while starting the service

ver 0.5 
------------------
1. introduction of /etc/token/leader/tokenleader_settings.ini for hostname, port etc.  
2. tokenleader-start  to start the service  
3. service can be started with ssl - although this will be mostly done by a nginx or apache in a production setup.  


What it does 
===================================================================
tokenleader has three simple operations:
1) recieves users request ,  autehnticates her and provides a  token  which carries  more users informations such as 
	a) user's roles ( one user can have multiple roles, although most of the cases one will suffice)  
	b) user is  also mapped with  a wfc ( work function context)  
	 wfc is a combination of  organization name, organization unit name   departname 

A typical token request call is : 
  
	curl -X POST -d '{"username": "admin", "password": "admin"}'  \
	-H "Content-Type: Application/json"  localhost:5001/token/gettoken

The validity period of the token can be set through the settings.ini in future , currently it is fixed as one hour.

Before a token can be recived ,   user need to be registered in the token leader server following the steps shown 
later section of this docuement.

2) receives a token from user , can validate and unencrypt the users information. 

3) maintains a catalog for all the microservies . The entry for services , it includes service name ,
   servie account password ( we have to see if this is required at all) , url for the service endpoint.
   A client can query tokenleader by service name and will thus get the url for the service .
   
   For each service end point three url can be registered , one for internal , this is  the default url .
   External url , when you want to segregate the users network from service network 
   and another is admin network , which can be further separated from the above two network
   

token can be used for authenticating an user wiithout the need for user to enter password  

To verify token:
  
 	curl -H  "X-Auth-Token:<paste toekn here>"  localhost:5001/token/verify_token  
 	
 tokenleader has a client which is automatically installed with the server , this provides a python api for 
 making hte call and verifying the token. The client also has the RBAC enforcer for authorization.
 read more about the client here -
  
   https://pypi.org/project/tokenleaderclient  
   https://github.com/microservice-tsp-billing/tokenleaderclient  
   
 
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
		@authclient.enforce_access_rule_with_token(<'rulename'> )
		def acl_enforcer_func_for_test(wfc=None):
		'''
		the rule name in this case should be :
		'pkgname.modulename.classname.acl_enforcer_func_for_test'
		for each api route functions the parameter wfc must be present
		'''
		    msg = ("enforcer decorator working ok with wfc org = {},"
		            "orgunit={}, dept={}".format(wfc.org, wfc.orgunit, wfc.department))
		  
		    return msg
	  
In the above example, the decorator  impose aceess control on the route /test1 . 

role name for the user  is retrived from the token leader , compared with the rule to acl map yml file 
(/etc/tokenleaderclient/role_acl_map_file.yml) which is maintained locally in the server where the service is running .

the role_to_acl_map file maps the  api route function names to and looks like :
- name: role1
  allow:
  - pkgname.modulename1.acl_enforcer_func_for_test
  - pkg1.module1.acl_enforcer_func_for_test
 
 check the sample data  and test cases  inside the tokenleaderclient for better understanding.
 tokenleader server ( this repo) it self uses  the tokenleader client for enforcing the rbac for 
 many api routes , for example adding users , listing users etc. Check the 
 tokenleader/app1/adminops/adminops_restapi.py file to get a better understanding or mail me
 your query at bhujay.bhatta@yahoo.com
 
  

decorator alos retrived work function context for the  user from tokenleader and passed it to 
original route function acl_enforcer_func_for_test .   The route function mandatorily to have a 
parameter called wfc as argument for the wfc , to get the value from the decorator.

now within the acl_enforcer_func_for_test  funtion  , wfc attributes like org, orgunit and department is used
to display a message. They actually  to be used for database query filtering so that based on the work function
user is able to view only relevant information.


Please follow the installation and configuration steps  
======================================================================================  

	virtualenv -p python3 venv  
	
	source venv/bin/activate  
	
	pip install --upgrade pip  
	
	pip install tokenleader 
	
	ssh-keygen < press enter to select all defaults>  
	
	
configure the /etc/token/leader/tokenleader_settings.ini
	
	sudo vi /etc/token/leader/tokenleader_settings.ini
	
	[flask_default]
	host_name = localhost
	host_port = 5001
	# sslnot required  since the production depoyment will be behind the apache with ssl 
	# This is required only when flask is started  without apache for testing
	ssl = enabled   
	ssl_settings = adhoc
	
	[token]
	# default will take the id_rsa keys from the  users home directory and .ssh directiry
	# put the file name here if  the file name is different
	#also the public ley need to be copied in the client settings file under /etc/tlclient
	private_key_file_location = default
	public_key_file_location = default
	
	[db]
	#change the database string  as appripriate for your porduction environment
	#contributors are requested to put some more example here
	SQLALCHEMY_DATABASE_URI = sqlite:////tmp/auth.db
	SQLALCHEMY_TRACK_MODIFICATIONS = False

	
all tokens will be encrypted by the private key and the  tokenleaderclient should have the public key in the 
general_settings.yml file so that token leader client can unencrypt the token using the public key


	register a admin  role  and a admin user 
	
	also two yml files in the /etc/.... folder as mentioned below
	
start the service :
	
	tokenleader-start

ensure  the port  of the server is open from security group.   
In production scnerio the service should be running with apache or ngnix or.  
 All of them can be bundled in a docker container , ( will be published soon)



TO set up the tokenleqder the following entities need to be registered in sequence   
from the root directory of  tokenleader  
====================================================================================

	 adminops  -h  provides help to understand the various options of admin funciton os tokenleader  
	
	 adminops   add  org   -n org1  
	 adminops   add  ou   -n ou2  
	 adminops   add  dept   -n  dept1  
	 adminops   addwfc -n wfc1 --wfcorg org1 --wfcou ou1 --wfcdept dept1 
	 adminops   list  wfc  -n wfc2  
	 #3 wfc2 <WorkFunctionContext wfc2 <Organization org1> <OrgUnit ou1> <Department dept1> >  
	  
	 adminops   add  role  -n role1   
	  
	 adminops adduser -n user10 --password user10 --emailid user10 --rolenames role10  --wfc wfc1
	 
	 adminops   list  user  -n all  or   adminops   list  user  -n user1
	 
	 adminops   list  dept  -n all   or  adminops   list  dept  -n dept1 
	 
	 adminops delete user -n user10  for deleting the user 
	 
	 
	 adminops  addservice  -n tokenleader --password tokenleader --urlint localhost:5001
	
	
	 adminops listservice -n all
	#{'name': 'micros1', 'endpoint_url_internal': None, 'id': 1, 'endpoint_url_external': 'localhost:5002', 'endpoint_url_admin': None}
	
	 adminops deletservice -n servie1
	 
	 
to add the admin user and admin role , the cli  command need to be run from the servers  local shell. However for subsequent 
operations there are  adminops rest api avialble 

	<url>:5001/list/users 
	/list/user/<username>
	/add/user

development is in progresss to make all the adminops oopeartons thourg rest api and also make them avialable from the 
tokenleader client
 
 there are two more files that need to be configured on the server for additonal operations such as adding user through 
 the rest call. 
 ===============================================================================
 
	 /etc/tlclient/general_configs.yml
	 /etc/tokenleader/service_access_policy.yml
 
 
 
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




To generate token :  
===================================================

	curl -X POST -d '{"username": "admin", "password": "admin"}'  \
	-H "Content-Type: Application/json"  localhost:5001/token/gettoken

what you get from tokenleader:
========================================

	{'service_catalog': {  
		'microservice1': {'id': 1,  
							'name': 'microservice1',  
							'endpoint_url_external': 'localhost/5000',  
							'endpoint_url_admin': 'localhost/5000',  
							'endpoint_url_internal': 'localhost/5000'}},   
	'message': 'success',   
	'auth_token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzUxMiJ9.eyJpYXQiOjE1NDk4Njg5MDYsInN1YiI6eyJpZCI6MSwiZW1haWwiOiJ1MUBhYmMuY29tIiwicm9sZXMiOlsicm9sZTEiXSwid2ZjIjp7ImlkIjoxLCJuYW1lIjoid2ZjMSIsIm9yZyI6Im9yZzEiLCJvcmd1bml0Ijoib3UxIiwiZGVwYXJ0bWVudCI6ImRlcHQxIn0sInVzZXJuYW1lIjoidTEifSwiZXhwIjoxNTQ5ODcyNTA2fQ.BBtTUcu8kUz__sbHmC8sB111C4Yzk6Fth5DjOoLCCTygqDjj-gQOS3x6T7e8rpKmHtf0LrDWPWFCmhIIqD2I8DuK4U4b-Hk7gbKYIVsvqL3DksOVF2SSe_6v4nNbJR50Q8mYrYQz0yijj-KQHj0Gc1FVCaBSXeIbA-uAUmSpQKCBDRqJbayK85e4dSoILpKL_Q1_JT4qqM7OwnGq05akJrosohNGKxp46gBex9l5iTPkoRgvQk-p1H61MMTdLKZIr9CmjIReXBBzfla6LoX8Siur_Lb4o1r0PJUcok-w69h_QCEqLe9VX9e4zFWnXIpDj5nwKqnj0JRKNvMw5VTcHA', 
	'status': 'success'}  



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



Testing 
===========================================================================
clone from git and then run 

	python -m unittest discover tests    

to run single unit test 
 
	python -m unittest tokenleader.tests.unittests.test_admin_ops.TestAdminOps.test_abort_delete_admin_user_input_not_yes  

for token generation and verification  testing this is a useful test  

	python -m unittest tokenleader.tests.test_auth.TestToken.test_token_gen_n_verify_success_for_registered_user_with_role   


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



