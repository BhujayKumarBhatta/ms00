Please take a note on the change log in the bottom of the document in case you  had used a previous version

Quick Start
=============================
for installation and configuration of docker with environment behind proxy , see the sectiom at the bottom of the 
page labeled as docker installation
	
	echo '10.174.112.106   lcldockerreg'  >> /etc/hosts
	echo '10.174.112.100   testldapserver100' >> /etc/hosts
	docker pull lcldockerreg:5000/tokenleader2               (optional)
	docker run -d -p 5001:5001  --add-host=tldbserver130:10.174.112.130 --name tokenleader  -v tokenleader_vol:/tmp lcldockerreg:5000/tokenleader2        (first goes and check from local registry and if not found goes to docker.io)

for post installation activity, to access files in container

	docker exec -it tokenleader 'bash'
	
change the tl_url to https

	vi /etc/tokenleader/client_configs.yml
	
	tokenleader  gettoken
	adminops  addservice  -n tokenleader --password tokenleader --urlint https://192.168.111.131:5001  --urlext https://192.168.111.131:5001
	adminops  addservice  -n LinkInventory --password LinkInventory --urlint https://192.168.111.131:5004 --urlext https://192.168.111.131:5004
	adminops  addservice  -n micros1 --password micros1 --urlint https://192.168.111.131:5002 --urlext https://192.168.111.131:5002
	
it is installed with default user user1, password user1  with role as role1 and domain default

once it is running install the client in a venv and test the features . 
consult the client installation doc  https://gitlab.net.itc/tsp-billing/tokenleaderclient

Mail server and Mail client local setup
========================================

run smtp server (arbitrary) as: nohup python smtpsinkserver.py > arbsmtpservlog.out 2>&1
will generate arbsmtpservlog.out in the current directory

run the smtp client for otp as: nohup python smtpclient.py &
will generate nohup.out in the current directory

Manual installation steps
=================================
optional Steps:  
-----------------------------------
	
	virtualenv -p python3 venv  
	
	source venv/bin/activate  
	
	pip install --upgrade pip

when running from source (git clone):
-----------------------------------
	cd tokenleader/
	
	pip install -r requirements.txt

installation:
-----------------------------------
	pip install tokenleader   (activate virtualenv venv, if required)

required configurations
========================
create  the following  directories and files under /etc folder. 

1. ssh-keygen < press enter to select all defaults>  
2. /etc/tokenleader/tokenleader_configs.yml
3. /etc/tokenleader/role_to_acl_map.yml
4. /etc/tokenleader/client_configs.yml
5. tokenleader-auth  -p <password of  tokenleader user>



sample configuration of each files
=============================================================================
configure the /etc/tokenleader/tokenleader_configs.yml
=============================================================================

    sudo mkdir /etc/tokenleader	
    sudo vi /etc/tokenleader/tokenleader_configs.yml

	flask_default:
       host_name: '0.0.0.0' # for docker this should 0.0.0.0
       host_port: 5001
       ssl: disabled # not required other than testing the flask own ssl. ssl should be handled by apache
       ssl_settings: adhoc

    database:
       Server: 10.174.112.130
       Port: 3306
       Database: auth
       UID: root
       db_pwd_key_map: db_pwd
       #engine_connect_string: 'mssql+pymysql:///{0}'

    domains:
       - default:
          auth_backend: default
          otp_required: False
       - itc:
          auth_backend: ldap   
          ldap_host: remote   # configure later with AD
          ldap_port: 389
          ldap_version: 3 
          DC1: test
          DC2: tspbillldap
          DC3: itc
          OU: Users
          O: itc   # configure later with AD
          otp_required: False
      
       - tsp:
          auth_backend: ldap   
          ldap_host: localhost     #10.174.112.100 if localhost doesnt work
          ldap_port: 389
          ldap_version: 3 
          DC1: test
          DC2: tspbillldap
          DC3: itc
          OU: Users
          otp_required: True

    listoftsp:
       - TATA
       - RELIANCE
       - BHARTI
       - SIFY
       - VODAFONE

    mailservice:
        Server: 10.174.112.79     #localhost if CALDOMINO & BLRDOMINO has not got access from 79
        Port: 5000

    otp:
        TATA: 10
        RELIANCE: 20
        BHARTI: 30
        SIFY: 20
        VODAFONE: 20
        org2: 10
        
    token:
        tokenexpiration: 30
        #default will take the id_rsa keys from the  users home directory and .ssh directiry
        #put the file name here if  the file name is different
        #also the public ley need to be copied in the client settings file under /etc/tlclient
        private_key_file_location: default
        public_key_file_location: default
        #use full path when deployed with apache
        #private_key_file_location: /home/sbhattacharyya/.ssh/id_rsa
        #public_key_file_location: /home/sbhattacharyya/.ssh/id_rsa.pub
        
    secrets:
        user_auth_info_file_location: tokenleader/tests/testdata/secrets.yml # where you have write access
        fernet_key_file: tokenleader/tests/testdata/fernet_key_file.yml # where you have write access and preferably separated from secrets_file_location
        db_pwd_key_map: db_pwd # when using encrypt-pwd command use this value for --keymap
        tokenleader_pwd_key_map: tl_pwd


generate an encrypted password for the db(one time)
===========================================================================================
when running from source (git clone) encrypt-pwd command  is available from shell as python encrypt-pwd.sh or ./encrypt-pwd.sh 

when installed through pip:
----------------------------------------------------

    encrypt-pwd -k db_pwd -p <your password here>
	
/etc/tokenleader/role_to_acl_map.yml
============================================================================================

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
tl_public_key: copy the public key of the server  <cat sh/id_rsa.id> and paste  the key in the following file

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

		pip install tokenleaderclient --upgrade
		tokenleader-auth -p user1 
**in some systems , the permisson of the /etc/tokenleader/.... files need 777 access ( read , write and execute ) access other wise this and the other commands shown was failing.

the file , /home/bhujay/tlclient/user_settings.ini , will be auto  generated and will looks like this :    

		[DEFAULT]  		 
		tl_password = gAAAAABcYnpRqet_VEucowJrE0lM1RQh2j5E-_Al4j8hm8vJaMvfj2nk7yb3zQo95lBFDoDR_CeoHVRY3QBFFG-p9Ga4bkJKBw==

note that the  original password has been encrypted before  saving in the file. if the keyfile is lost or the 
password is forgotten   the  file has to be deleted and recreated. Accordingly the users password in the 
tokenleader server also to be changed. 

TO set up the tokenleader the following entities need to be registered in sequence   ( see the ** section )
from the root directory of  tokenleader, change the name of org , ou , dept , wfc , role and user as per your need
====================================================================================
when running from source (git clone) adminops command  is avilable from shell as python adminops.sh or ./adminops.sh 

	 adminops -h  provides help to understand the various options of admin function os tokenleader
	 adminops initdb 
	 adminops add  org   -n org1 (by default orgtype is internal)
	 adminops add  org   -n org2 --orgtype external
	 adminops add  ou   -n ou1 
	 adminops add  dept   -n  dept1  
	 adminops addwfc -n wfc1 --wfcorg org1 --wfcou ou1 --wfcdept dept1 	 
	 adminops list  wfc  -n wfc1
	 adminops add  role  -n role1  	  
	 adminops adduser -n user1 --password user1 --emailid user1 --rolenames role1  --wfc wfc1
	 adminops addservice  -n tokenleader --password tokenleader --urlint localhost:5001
	 adminops addservice  -n linkInventory --password tokenleader --urlint http://localhost:5004 --urlext https://localhost:5004
	 adminops addservice  -n micros2 --password tokenleader --urlint http://localhost:5003 --urlext https://localhost:5003
	 adminops addservice  -n micros1 --password tokenleader --urlint http://localhost:5002 --urlext https://localhost:5002

start the service :
==============================================================
when running from source (git clone) adminops command  is available from shell as python tokenleader-start.sh or ./tokenleader-start.sh 
	
	 tokenleader-start

CLI utilities 
====================================================================
using user name and password from config file

	tokenleader gettoken							for internal user only,
reads from client_configs and secrets or username and password can be supplied  through the CLI 
	
	tokenleader gettoken --authuser user1 --authpwd user1 --domain domainname
	tokenleader gettoken --authuser user1 --authpwd user1 --domain domainname --otp otpnum
	tokenleader gettoken --authuser user1 --authpwd user1											as domain is not mandate
	tokenleader gettoken --authuser user1 --authpwd user1 --otp otpnum
		
Other CLI operaions 

	tokenleader verify -t <paste the token here>
	tokenleader list -e <entity> -u <username> -p <password>					for internal user
	tokenleader list -e <entity> -u <common name of ldap> -o <otp>				for external user,
entity can be user, role, dept, org, ou, wfc etc.

    tokenleader add org -n <orgname> -u <username> -p <password>                       for internal user
    tokenleader add org -n <orgname> --orgtype external -u <username> -p <password>    for external user,
same for ou, dept and role.        

    tokenleader add org -n <orgname> -u <common name of ldap> -o <otp>				when external user adds it, if allowed in role_to_acl.yml
    tokenleader adduser -n <username> --password <password> --emailid <emailid> --rolenames <role1,role2> --wfc <wfcname> -u <common name of ldap> -o <otp>				when external user adds it, if allowed in role_to_acl.yml
 
 
Python client 
======================================================================================
From python shell it works as follows:

    from tokenleaderclient.configs.config_handler import Configs    
	from  tokenleaderclient.client.client import Client 
		
		
this will read  the credentials from configurations file. Will be used for CLI. 
 
	auth_config = Configs()  	  (file has user as user1 and password as user1; and domain is hardcoded as default cause host organisation's user authenticates using local db)
		
the user name and password will be  taken from the input  but rest of the settings will be from config files.  
This will be used for browser based login  

	auth_config = Configs(tlusr='user1', tlpwd='user1', domain='default') 
		
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
		   - tokenleader.list_users
		   - tokenleader.list_user_byname
		   - tokenleader.list_org
		   - tokenleader.list_dept
		   - tokenleader.list_role
		   - tokenleader.list_ou
		   - tokenleader.list_wfc
		   - tokenleader.add_user
		   - tokenleader.add_wfc
		   - tokenleader.add_ou
		   - tokenleader.add_dept
		   - tokenleader.add_org
		   - tokenleader.add_role
		   - tokenleader.delete_user
		   - tokenleader.delete_org
		   - tokenleader.delete_ou
		   - tokenleader.delete_dept
		   - tokenleader.delete_role
		   - tokenleader.delete_wfc
		   - tokenleader.list_services
		   - tokenleader.list_services_byname
		   - tokenleader.add_service
		   - tokenleader.delete_service
		   - tokenleader.delete_service_byname
	   		  
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
1) recieves users request ,  authenticates her and provides a  token  which carries  more users informations such as 
	a) user's roles ( one user can have multiple roles, although most of the cases one will suffice)  
	b) user is  also mapped with  a wfc ( work function context)  
	 wfc is a combination of  organization name, organization unit name   departname 

A typical token request call is : 
  
	curl -X POST -d '{"username": "admin", "password": "admin"}'  \
	-H "Content-Type: Application/json"  localhost:5001/token/gettoken

The validity period of the token can be set through the settings.ini in future , currently it is fixed 30 seconds.

Before a token can be recived ,   user need to be registered in the token leader server following the steps shown 
later section of this docuement.

2) receives a token from user , can validate and unencrypt the users information. 

3) maintains a catalog for all the microservices . The entry for services , it includes service name ,
   service account password ( we have to see if this is required at all) , url for the service end-point.
   A client can query tokenleader by service name and will thus get the url for the service.
   
   For each service end point, three url can be registered, one for internal, this is the default url.
   External url, when you want to segregate the users network from service network 
   and another is admin network, which can be further separated from the above two network.
   
token can be used for authenticating an user without the need for user to enter password  

To verify token:
  
 	curl -H  "X-Auth-Token:<paste token here>"  localhost:5001/token/verify_token  
 	
 tokenleader has a client which is automatically installed with the server , this provides a python api for 
 making the call and verifying the token. The client also has the RBAC enforcer for authorization.
 read more about the client here -
  
   http://10.174.112.140/packages/
   https://gitlab.net.itc/tsp-billing/tokenleaderclient  
   
Why token service and how it works
======================================================================================
 in situations where a service or a client need to make several  http /REST call to an 
 application/service(microservice)/server or  to multiple applications/services/servers, 
 sending the user name and password repeatedly over the http traffic is not desirable, neither it is good
 to store the user name and password in servers session for a stateless application. In these cases token based 
 authentication helps.
 
 Once an user or service obtain a token, subsequent calls to the server or even to different servers can be made
 using the token instead of username and password. The server then will make a validation call to tokenleader for 
 authentication and also will retrieve role name and wfc information. 
 
 The information retrieved  from the token leader then can be used by the server for granting proper authorization to the 
 server resources . Therefore authentication is handled  by the tokenleader application whereas the authorization is handled 
 by the application being served to the user. 
 
 each application uses a local role to acl map. For each api route there is one acl name which either deny or permits the 
 http call to the  api route . further  to control how much data to be given access to the user , the wfc details  will be 
 used for filtering  the data query ( mainly data persistance and query)

To generate token using curl :  
===================================================

	curl -X POST -d '{"username": "admin", "password": "admin", "domain": "default"}'  \
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

 	curl -H  "X-Auth-Token:<paste token here>"  localhost:5001/token/verify_token  

How the verified token data looks like :
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

For  development machine with sqlite db , there are challenges in migration due to limitation of database
alter capabilities inherent to sqlite. So sometimes , deleting the migration folder and and  recreating a   
fresh migration helped.


Testing 
===========================================================================
clone from git and then run

	python -m unittest discover tests  (ImportError: No module named 'tokenleader') --> 1
	python -m unittest tokenleader.tests.test_catalog_ops  (Recommended instead of 1)

to run single unit test
 
	python -m unittest tokenleader.tests.unittests.test_admin_ops.TestAdminOps.test_abort_delete_admin_user_input_not_yes (ImportError: No module named 'tokenleader.tests.unittests') --> 2 
    python -m unittest tokenleader.tests.test_admin_ops.TestUserModel.test_delete_org  (Recommended instead of 2)

for token generation and verification  testing this is a useful test

	python -m unittest tokenleader.tests.test_auth.TestToken.test_token_gen_n_verify_success_for_registered_user_with_role

Deployment
===========================================

	sudo apt-get install -y  python3-dev apache2 apache2-dev
	
	sudo su 
	
	source venv/bin/activate
	
	pip install mod_wsgi
	 
	mod_wsgi-express module-config
	 
	mod_wsgi-express install-module

this will print the following lines : 	
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

 **** Install DOCKER ****
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
	Environment="HTTP_PROXY=http://10.172.100.14:3128/" "HTTPS_PROXY=http://10.172.100.14:3128/" "NO_PROXY=localhost,127.0.0.1,10.174.112.106"       (mention all microservice, other components host IP/hostname in NO_PROXY)

	sudo systemctl daemon-reload
	sudo systemctl restart docker
	systemctl show --property=Environment docker


Tokenleader specific 
=================================================
docker run -d -p 5001:5001  --add-host=tldbserver130:10.174.112.130 --name tokenleader  -v tokenleader_vol:/tmp lcldockerreg:5000/tokenleader2

docker exec -it {CONTAINER ID of tokenleader} "/bin/bash"

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
=============================================
tests/testdata/test_tokenleader_configs.yml   have changed 

secrets:
     user_auth_info_file_location: testlocation # for testing tokenleader client 1.5.1 is required  to detect 'testlocation'. the files under tests/testdata will be 
     autodetected     
     fernet_key_file: testlocation # do
 
a pre generated secrets.yml for db_pwd as welcome@123 will be placed here in tesdata
db_pwd: gAAAAABdCgpm0oJ07suvMLtvg-8CkyMfynhs8ngCOp8R0sDjaPPKK5YrETXpd7NUszSqIDWYOv1jrKUu6u7r5ly0qk1PbKnDYQ==

tests/testdata/test_client_configs.yml will be also there

these files and the changes made  in config_handler will ensure following tests will be success without the need for /etc/tokenleader/files which are required for production.

1. test_configs.py
2. all other tests except the *_restapi.py 

however  tests mentioned in point 2 are linked to base_test.py which imports 
from tokenleader.app1.adminops.adminops_restapi import adminops_bp
this necessitates all the config files under /etc/tokenleader as well 


version 2.3
-----

add service had a bug for admin url not gettinng added

version2.2
-----------------
catalogbp was moved to restapi and hence error in import

version2.1
-----------------
catalog_bp was not included in the app_run resulitng 404 for catalog ops

ver 1.9
--------
introducing domain and otp 
domain to  auth_backend database or ldap map made configurable in yml
authentication and token generation class separated 
api routes module separated


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

