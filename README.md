Please take a note on the change log in the bottom of the document in case you  had used a previous version

Quick Start
=============================
for installation and configuration of docker with environment behind proxy , see the sectiom at the bottom of the 
page labelled as docker installation
	
	docker pull bhujay/tokenleader:1.8 
	docker run -d -p 5001:5001  --name tokenleader  -v tokenleader_vol:/tmp bhujay/tokenleader:1.8 
	
	docker exec -it tokenleader 'bash'
	
change the tl_url to https


	vi /etc/tokenleader/client_configs.yml
	
	tokenleader  gettoken
	adminops  addservice  -n tokenleader --password tokenleader --urlint https://192.168.111.131:5001  --urlext https://192.168.111.131:5001
	adminops  addservice  -n LinkInventory --password LinkInventory --urlint https://192.168.111.131:5004 --urlext https://192.168.111.131:5004
	adminops  addservice  -n micros1 --password micros1 --urlint https://192.168.111.131:5002 --urlext https://192.168.111.131:5002
	
	
	
	
it is installed with default user use1 and password user1  with role as role1 

once it is running install the client in a venv and test the features . 
consult the client installation doc  https://github.com/microservice-tsp-billing/tokenleaderclient


Manual installation steps
=================================
optional Steps:  
-----------------------------------
	
	virtualenv -p python3 venv  
	
	source venv/bin/activate  
	
	pip install --upgrade pip  

installtion:
-----------------------------
	pip install tokenleader ( create virtual env if required)

required configurations
========================
create  the following  directories and files under /etc folder. 

1. ssh-keygen < press enter to select all defaults>  
2. /etc/tokenleader/tokenleader_settings.ini
3. /etc/tokenleader/role_to_acl_map.yml
4. /etc/tokenleader/client_configs.yml
5. tokenleader-auth  -p <password of  tokeneader user>


sample configuration of each files
=============================================================================
configure the /etc/tokenleader/tokenleader_settings.ini
=============================================================================
   
    sudo mkdir /etc/tokenleader	
	sudo vi /etc/tokenleader/tokenleader_settings.ini
	
	[flask_default]
	host_name = localhost
	host_port = 5001
	# ssl not required  since the production deployment will be behind the apache with ssl 
	# This is required only when flask is started  without apache for testing
	# put enabled  for enabling ssl 
	ssl = disabled   
	ssl_settings = adhoc
	
	[token]
	# default will take the id_rsa keys from the  users home directory and .ssh directiry
	# put the file name here if  the file name is different
	#also the public ley need to be copied in the client settings file under /etc/tlclient
	private_key_file_location = default 
	public_key_file_location = default
	#use full path when deployed with apache 
	#private_key_file_location = /home/bhujay/.ssh/id_rsa
	#public_key_file_location = /home/bhujay/.ssh/id_rsa.pub
	
	[db]
	#change the database string  as appripriate for your production environment
	#contributors are requested to put some more example here
	SQLALCHEMY_DATABASE_URI = sqlite:////tmp/auth.db
	SQLALCHEMY_TRACK_MODIFICATIONS = False
	
/etc/tokenleader/role_to_acl_map.yml
============================================================================================
	
      sudo mkdir /etc/tokenleader      
      sudo vi /etc/tokenleader/role_to_acl_map.yml
	 
	  maintain at least one role and one entry in the following format 
	 
		- name: role1
		  allow:
		  - tokenleader.adminops.adminops_restapi.list_users		  
		  
		- name: role2
		  allow:
		  - service1.third_api.rulename3
		  - service1.fourthapi_api.rulename4
/etc/tokenleader/client_configs.yml which holds the non secret configs  about the client and looks as
================================================================================================
user_auth_info_file_location: <change this location to users home dir , two files will be generated and stored here>
fernet_key_file: <same as above>
tl_public_key: copy the public key of the server  <cat sh/id_rsa.id> and paste  the key here 
        
        sudo vi 
        sudo vi /etc/tokenleader/client_configs.yml

		user_auth_info_from: file # OSENV or file , leave it as file
		user_auth_info_file_location: /home/bhujay/tlclient/user_settings.ini # change this location to users home dir 
		fernet_key_file: /home/bhujay/tlclient/prod_farnetkeys
		tl_public_key: ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQCYV9y94je6Z9N0iarh0xNrE3IFGrdktV2TLfI5h60hfd9yO7L9BZtd94/r2L6VGFSwT/dhBR//CwkIuue3RW23nbm2OIYsmsijBSHtm1/2tw/0g0UbbneM9vFt9ciCjdq3W4VY8I6iQ7s7v98qrtRxhqLc/rH2MmfERhQaMQPaSnMaB59R46xCtCnsJ+OoZs5XhGOJXJz8YKuCw4gUs4soRMb7+k7F4wADseoYuwtVLoEmSC+ikbmPZNWOY18HxNrSVJOvMH2sCoewY6/GgS/5s1zlWBwV/F0UvmKoCTf0KcNHcdzXbeDU9/PkGU/uItRYVfXIWYJVQZBveu7BYJDR bhujay@DESKTOP-DTA1VEB
		ssl_verify: False # leave it as is 		
		tl_user: user1
		tl_url: http://localhost:5001
		ssl_verify: False



users authentiaction information . The file is generated using  an cli   
=================================================================================

		pip install tokenleaderclient
		tokenleader-auth -p user1 
**in some systems , the permisson of the /etc/tokenleader/.... files need 777 access ( read , write and execute ) access other wise this and the other commands shown was failing.

the file , /home/bhujay/tlclient/user_settings.ini , will be auto  generated and will looks like this :    

		[DEFAULT]  		 
		tl_password = gAAAAABcYnpRqet_VEucowJrE0lM1RQh2j5E-_Al4j8hm8vJaMvfj2nk7yb3zQo95lBFDoDR_CeoHVRY3QBFFG-p9Ga4bkJKBw==

note that the  original password has been encrypted before  saving in the file. if the keyfile is lost or the 
password is forgotten   the  file has to be deleted and recreated. Accordingly the users password in the 
tokenleader server also to be changed. 

TO set up the tokenleqder the following entities need to be registered in sequence   ( see the ** section )
from the root directory of  tokenleader, change the name of org , ou , dept , wfc , role and user as per your need
====================================================================================
when running from source (git clone) adminops command  is avilable from shell as python adminops.sh or ./adminops.sh 

	 adminops  -h  provides help to understand the various options of admin function os tokenleader  
	 
	 adminops initdb 
	 
	 adminops   add  org   -n org1  
	 adminops   add  ou   -n ou1 
	 adminops   add  dept   -n  dept1  
	 adminops   addwfc -n wfc1 --wfcorg org1 --wfcou ou1 --wfcdept dept1 	 
	 adminops   list  wfc  -n wfc1
	 adminops   add  role  -n role1  	  
	 adminops adduser -n user1 --password user1 --emailid user1 --rolenames role1  --wfc wfc1
	 adminops  addservice  -n tokenleader --password tokenleader --urlint localhost:5001

start the service :
==============================================================
when running from source (git clone) adminops command  is avilable from shell as python tokenleader-start.sh or ./tokenleader-start.sh 
	
	tokenleader-start
	
Test it is working
=======================================================


CLI utilities 
====================================================================
using user name and password from config file 

		tokenleader  gettoken 
		
or username and password can be supplied  theough the CLI 

		gettoken  --authuser user1 --authpwd user1
		
Other CLI operaions 

		tokenleader  verify -t <paste the toen here>
		tokenleader  list user
 
 
Python client 
======================================================================================
From python shell it works as follows:

        from tokenleaderclient.configs.config_handler import Configs    
		from  tokenleaderclient.client.client import Client 
		
		
this will read  the credentials from configurations file. Will be used for CLI. 
 
		auth_config = Configs()  	
		
the user name and password will be  taken from the input  but rest of the settings will be from config files.  
This will be used for browser based login  

		auth_config = Configs(tlusr='user1', tlpwd='user1') 
		
Inititialize the client with auth_config
	 
		c = Client(auth_config)
		c.get_token()
		{'message': 'success', 'status': 'success', 'auth_token': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzUxMiJ9.eyJpYXQiOjE1NDk5NjcxODAsImV4cCI6MTU0OTk3MDc4MCwic3ViIjp7IndmYyI6eyJvcmd1bml0Ijoib3UxIiwibmFtZSI6IndmYzEiLCJkZXBhcnRtZW50IjoiZGVwdDEiLCJpZCI6MSwib3JnIjoib3JnMSJ9LCJlbWFpbCI6InVzZXIxIiwiaWQiOjEsInVzZXJuYW1lIjoidXNlcjEiLCJyb2xlcyI6WyJyb2xlMSJdfX0.gzW0GlgR9qiNLZbR-upuzgHMw5rOm2luV-EnHZwlOSJ-0kJnHsiiT5Wk-HZaqMGZd0YJxA1e9GMroHixtj7WJsbLLjhgqQ5H1ZprCkA9um6-vdkwAFVduWIqIN7S6LbsE036bN7y4cdgVhuJAKoiV1KyxOU1-Hxid5l3inL0Hx2aDUrZ3InzFKBw7Mll86xWdfkpHSdyVjVuayKQMvH2IdT3N15k4O2tSwV3t6UhG6MO0ngHFt3LFR471QWGzJ8UyRzqyqbheuk5vwPk684MfRclCtKx33LWAMf-HXQgVA2py_NzmEiY1ROsKmZqpbIO9YKIO_aFCmzB7DQSI8dcYg', 'service_catalog': {'tokenleader': {'endpoint_url_external': 'localhost:5001', 'endpoint_url_admin': None, 'id': 2, 'endpoint_url_internal': None, 'name': 'tokenleader'}, 'micros1': {'endpoint_url_external': 'localhost:5002', 'endpoint_url_admin': None, 'id': 1, 'endpoint_url_internal': None, 'name': 'micros1'}}}
		c.verify_token('eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzUxMiJ9.eyJpYXQiOjE1NDk5NjcxODAsImV4cCI6MTU0OTk3MDc4MCwic3ViIjp7IndmYyI6eyJvcmd1bml0Ijoib3UxIiwibmFtZSI6IndmYzEiLCJkZXBhcnRtZW50IjoiZGVwdDEiLCJpZCI6MSwib3JnIjoib3JnMSJ9LCJlbWFpbCI6InVzZXIxIiwiaWQiOjEsInVzZXJuYW1lIjoidXNlcjEiLCJyb2xlcyI6WyJyb2xlMSJdfX0.gzW0GlgR9qiNLZbR-upuzgHMw5rOm2luV-EnHZwlOSJ-0kJnHsiiT5Wk-HZaqMGZd0YJxA1e9GMroHixtj7WJsbLLjhgqQ5H1ZprCkA9um6-vdkwAFVduWIqIN7S6LbsE036bN7y4cdgVhuJAKoiV1KyxOU1-Hxid5l3inL0Hx2aDUrZ3InzFKBw7Mll86xWdfkpHSdyVjVuayKQMvH2IdT3N15k4O2tSwV3t6UhG6MO0ngHFt3LFR471QWGzJ8UyRzqyqbheuk5vwPk684MfRclCtKx33LWAMf-HXQgVA2py_NzmEiY1ROsKmZqpbIO9YKIO_aFCmzB7DQSI8dcYg')
		{'payload': {'iat': 1549967180, 'exp': 1549970780, 'sub': {'username': 'user1', 'roles': ['role1'], 'id': 1, 'email': 'user1', 'wfc': {'orgunit': 'ou1', 'id': 1, 'org': 'org1', 'department': 'dept1', 'name': 'wfc1'}}}, 'message': 'Token has been successfully decrypted', 'status': 'Verification Successful'}
		


for RBAC configure  /etc/tokenleader/role_to_acl_map.yml
============================================================================================
	
      sudo mkdir /etc/tokenleader 
      sudo vi /etc/tokenleader/role_to_acl_map.yml
	 
	  maintain at least one role and one entry in the following format 
	 
		- name: role1
		  allow:
		   - tokenleader.adminops.adminops_restapi.list_users		
		   - tokenleader.adminops.adminops_restapi.list_org		
		   - tokenleader.adminops.adminops_restapi.list_ou	
		   - tokenleader.adminops.adminops_restapi.list_role		
		   - tokenleader.adminops.adminops_restapi.list_dept	  
		  
		- name: role2
		  allow:
		  - service1.third_api.rulename3
		  - service1.fourthapi_api.rulename4

		from tokenleaderclient.rbac.enforcer import Enforcer
		enforcer = Enforcer(c)
		
Here c is the instance of  Client() , the tokenleadercliet which we have initialized in the previous
example of python client.  

Now @enforcer.enforce_access_rule_with_token('rulename1') is avilable within any flask application  
where tokenleader client is installed.   



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

List of api routes and their rules
============================================================================
1. /list/users     acl rule name - tokenleader.adminops.adminops_restapi.list_users






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




To generate token using curl :  
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
	flask db upgrade   

if there is a change in db structure, and a migration is done , commit and push the migration directory to the git  
from the  machine where migration was done.  

For  development machine with sqllite db , there are chalenges in migration due to lil8mitiaton of database
alter capabilities inherent to sqllite. So sometimes , delelting the migration folder and and  recreating a   
fresh migartion helped.




Deployment
===========================================

	sudo apt-get install -y  python3-dev apache2 apache2-dev
	
	sudo su 
	
	source venv/bin/activate
	
	pip install mod_wsgi
	 
	mod_wsgi-express module-config
	 
	mod_wsgi-express install-module

this will print the folowing lines : 	
LoadModule wsgi_module "/usr/lib/apache2/modules/mod_wsgi-py35.cpython-35m-x86_64-linux-gnu.so"  - copy this to wsgi.load
WSGIPythonHome "/mnt/c/mydev/microservice-tsp-billing/tokenleader/venv" copy this to wsgi.conf  

	vi /etc/apache2/mods-available/wsgi.conf
	
	vi /etc/apache2/mods-available/wsgi.load
	
	cd /etc/apache2/mods-enabled/
	
	ln -s ../mods-available/wsgi.conf  wsgi.conf
	
	ln -s ../mods-available/wsgi.load  wsgi.load
	
	sudo a2enmod ssl 
	
	sudo mkdir /etc/apache2/ssl
	
	sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
	 -keyout /etc/apache2/ssl/tokenleader-apache-server.key  \
	 -out /etc/apache2/ssl/tokenleader-apache-server.crt
	
	
	apachectl configtest 

download the copy of app.wsgi file and copy it in /var/www
download the tokenleader-apache.conf , place it in /etc/apache2/sites-enabled/  and modify the  
directories  and the username 

start the apache service 

    sudo service apache2 start
    
	
    
  
 
 https://pypi.org/project/mod_wsgi/
 
 important note :  https://modwsgi.readthedocs.io/en/develop/user-guides/virtual-environments.html   
 ===========================
	



development
===========================================================

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






 **** Install DOCKER
 ===================================================================================

	sudo apt-get update
	
	apt-get install \
	    apt-transport-https \
	    ca-certificates \
	    curl \
	    gnupg-agent \
	    software-properties-common
	
	curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
	sudo apt-key fingerprint 0EBFCD88




	sudo add-apt-repository \
	   "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
	   $(lsb_release -cs) \
	   stable"
	
	sudo apt-get update
	
	sudo apt-get install docker-ce docker-ce-cli containerd.io
	
	apt-cache madison docker-ce
	
	sudo apt-get install docker-ce=5:18.09.2~3-0~ubuntu-xenial docker-ce-cli=5:18.09.2~3-0~ubuntu-xenial containerd.io
	
	 
	vi ~/.docker/config.json



	{
	 "proxies":
	 {
	   "default":
	   {
	     "httpProxy": "http://10.172.100.14:3128",
	     "httpsProxy": "http://10.172.100.14:3128",
	     "noProxy": "*.test.example.com,.example2.com"
	   }
	 }
	}
	
	
	sudo groupadd docker
	sudo usermod -aG docker $USER
	






	sudo mkdir -p /etc/systemd/system/docker.service.d
	vi /etc/systemd/system/docker.service.d/http-proxy.conf
	[Service]
	Environment="HTTP_PROXY=http://10.172.100.14:3128/" HTTPS_PROXY=http://10.172.100.14:3128/"

	sudo systemctl daemon-reload
	sudo systemctl restart docker
	systemctl show --property=Environment docker


Tokenleader speific 
=================================================
docker run -d -p 10.174.112.83:5001:5001 bhujay/tokenleader:1.8

docker exec -i -t 8aa561c09458 /bin/bash


adminops addservice -n micros1 --password micros1 --urlint http://10.174.112.83  --urlext  http://10.174.112.83





tl_public_key: ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDENN9QYdy6RUEJUsOcGECj+7uvyhHlNaZqVN5YcP/MCxBIEoWD3ewu1bQxqW/xC938gHXGZ7NWncv+u9IADwmVYBD8/hYUWJFOKFOKtt8+ZcAFamAz6qGAmKFUnThZ5C/n1PAwS8L03aj62NfxXTjgpohcKRn3Pq9SW7TNgeApn3RSkGoydKJOqo8GeNnKuDxJMHhkR663pLtYH+VOvE/TzethQn64Xc1/HL02o6HRsCWtI0UXev2RLMsVa/wP0k2ItUi7YnmZPyL6ATfeiHIRrRmfDsidqUA6eNZ+fsdw6dO6H0TGggeYd+d8I14PBTx6zYwL+QIEiqNBxP6nIdMp bhujay@DESKTOP-DTA1VEB


user_auth_info_from: file # OSENV or file
user_auth_info_file_location: /home/cloud/secrets
fernet_key_file: /home/cloud/farnetkeys

tl_public_key: ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDENN9QYdy6RUEJUsOcGECj+7uvyhHlNaZqVN5YcP/MCxBIEoWD3ewu1bQxqW/xC938gHXGZ7NWncv+u9IADwmVYBD8/hYUWJFOKFOKtt8+ZcAFamAz6qGAmKFUnThZ5C/n1PAwS8L03aj62NfxXTjgpohcKRn3Pq9SW7TNgeApn3RSkGoydKJOqo8GeNnKuDxJMHhkR663pLtYH+VOvE/TzethQn64Xc1/HL02o6HRsCWtI0UXev2RLMsVa/wP0k2ItUi7YnmZPyL6ATfeiHIRrRmfDsidqUA6eNZ+fsdw6dO6H0TGggeYd+d8I14PBTx6zYwL+QIEiqNBxP6nIdMp bhujay@DESKTOP-DTA1VEB



tl_user: user1
tl_url: https://localhost:5001
ssl_verify: False
 
	



change log 
================================================

ver 1.5
----------------
tokenleader 0.70  and few fixes

ver1.3
-------------
1. migration/version was missing 
2. Sample config files created under etc directory in  source code

ver 1.1 
-------------

1. all configs are in /etc/tokenleader
2. tlclient command changed to tokenleader
3. tlconfig command changed to tokenleader-auth

ver 1.0
----------------
setting FLASK_APP  during db init 


ver 0.8 / 0.9
------------------
1. added adminops initdb  command  for  applying the changes  in database schema

ver 0.7 
--------------
1. tokenleaderclient bug resolved in client version 0.64

ver 0.6
--------------
1. check  presence of required parameters in /etc/tokenleader/tokenleader_settings.ini while starting the service

ver 0.5 
------------------
1. introduction of /etc/tokenleader/tokenleader_settings.ini for hostname, port etc.  
2. tokenleader-start  to start the service  
3. service can be started with ssl - although this will be mostly done by a nginx or apache in a production setup.  

