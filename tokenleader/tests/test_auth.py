import time
import datetime
import json
from flask import current_app
from tokenleader.app1 import db
import random
from tokenleader.app1.authentication.tokenmanager import TokenManager
from tokenleader.app1.authentication.authenticator import Authenticator
from tokenleader.tests.admin_ops import TestUserModel
# from tokenleader.app1 import db
from tokenleader.app1.authentication.models import User, Role, Workfunctioncontext, Organization, Orgunit, Department, Otp
from tokenleader.app1.adminops import admin_functions as af
# from tokenleader.tests.test_catalog_ops import TestCatalog , service_catalog
# tc = TestCatalog()



class TestToken(TestUserModel):
    '''
    (venvp3flask) bhujay@DESKTOP-DTA1VEB:/mnt/c/mydev/myflask$ python -m unittest discover tests
    '''
    EMAIL_TEST='Srijib.Bhattacharyya@itc.in'
 
    def test_auth_token_with_actual_rsa_keys_fake_user(self):    #TOKEN GEN, VERIFY AND EXPIRY:working     
        tm = TokenManager(self.user_from_db)
        publickey = current_app.config.get('public_key')
        auth_token = self.get_auth_token_with_actual_rsa_keys_fake_user()
        self.assertTrue(isinstance(auth_token, bytes))
        np = tm.decrypt_n_verify_token(auth_token, publickey)
        self.assertTrue(isinstance(np, dict))
        self.assertTrue((np.get('payload').get('sub').get('wfc').get('org')) == 'default')
        #TODO: TOKEN EXPIRY TEST CAN BE RUN AT THE LAST SEPARATELY
        #time.sleep(1) #HIGHER THAN THE VALUE SET IN CONFIG FILE
        with self.client:
            self.headers = {'X-Auth-Token': auth_token}
            response = self.client.get(
                '/token/verify_token',
                headers=self.headers)
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] != 'Signature expired')
            self.assertTrue(isinstance('payload', str))
  
   
    def test_get_token_no_otp(self):  ##GET TOKEN WITH NO OTP REQUIREMENT ALSO VERIFY THE TOKEN: WORKING  
        '''
        user_creation_for_test method comes from parent class TestUserModel from test_admin_ops module
        this method registers an user with name as u1 
        '''
        u1 = self.user_creation_for_test()
        #tc.add_service()#print(u1.to_dict())
        data=json.dumps(dict(
                     username='u1',
                     password='Secret@12' ,
                     domain='org1'
                 ))
        with self.client:
            response = self.client.post(
                 '/token/gettoken', 
                 data=data,
                 content_type='application/json')
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'success')
            self.assertTrue('auth_token' in data)
            #self.assertTrue(data['service_catalog'] == service_catalog )
            mytoken = data['auth_token']
        ######################verify the token #########################
        with self.client:
            self.headers = {'X-Auth-Token': mytoken}
            response = self.client.get(
                '/token/verify_token',
                headers=self.headers)
            #print('response is {}'.format(response))
            data = json.loads(response.data.decode())
            # print(data)
            self.assertTrue(data['status'] == 'Verification Successful')
            self.assertTrue('payload' in data)
            roles_retrived_from_token = data['payload'].get('sub').get('roles')
            self.assertTrue(data['payload'].get('sub').get('username') == 'u1')
            self.assertTrue(data['payload'].get('sub').get('email') == 'u1@abc.com')
            self.assertTrue(data['payload'].get('sub').get('is_active') == 'Y')
            self.assertTrue(data['payload'].get('sub').get('allowemaillogin') == 'N')
            self.assertTrue(roles_retrived_from_token, list)#== ['test_role_1', 'test_role_2'])
            self.assertTrue(sorted(roles_retrived_from_token) == sorted(['role1']))
            self.assertTrue((data['payload'].get('sub').get('wfc').get('org')) == 'org1')
   
  
    def test_get_token_email_otp(self):    #####GET TOKEN USING OTP AND EMAIL AND VERIFY##############   : WORKING
        self.external_user_creation_for_test()
        data=json.dumps(dict(
                    username='u3',
                    password='Secret@12' ,
                    domain='org2'
                ))
        with self.client:
            response = self.client.post(
                '/token/gettoken', 
                data=data,
                content_type='application/json')
        data = json.loads(response.data.decode())
        userdet = User.query.filter_by(username='u3').first()
        otp = userdet.otp.otp
        data=json.dumps(dict(
                    email='u3@itc.in',
                    otp=otp
                ))
        with self.client:
            response = self.client.post(
                '/token/gettoken', 
                data=data,
                content_type='application/json')
        data = json.loads(response.data.decode())
        self.assertTrue(data['status'] == 'success')
        self.assertTrue('auth_token' in data)
        with self.client:
            self.headers = {'X-Auth-Token': data.get('auth_token')}
            response = self.client.get(
                '/token/verify_token',                
                headers=self.headers)
            #print('response is {}'.format(response))
            data = json.loads(response.data.decode())
            #print(data)
            self.assertTrue(data['status'] == 'Verification Successful')
            self.assertTrue('payload' in data)
            roles_retrived_from_token = data['payload'].get('sub').get('roles')
            self.assertTrue(data['payload'].get('sub').get('username') == 'u3')
            self.assertTrue(data['payload'].get('sub').get('email') == 'u3@itc.in')
            self.assertTrue(data['payload'].get('sub').get('is_active') == 'Y')
            self.assertTrue(data['payload'].get('sub').get('allowemaillogin') == 'Y')
            self.assertTrue(roles_retrived_from_token, list)#== ['test_role_1', 'test_role_2'])
            self.assertTrue(sorted(roles_retrived_from_token) == sorted(['role2']))
            self.assertTrue((data['payload'].get('sub').get('wfc').get('org')) == 'org2')
  
  
    def test_get_token_default_domain(self):   ###CALLING WITH NO DOMAIN WHILE USERS HAS BEEN REGISTERED WITH DEFAULT DOMAIN SHOULD SUCCESS: working
        self.user_default_domain_creation_for_test()
        data=json.dumps(dict(
                    username='user_default_domain',
                    password='Secret@12' ,
                ))
        with self.client:
            response = self.client.post(
                '/token/gettoken', 
                data=data,
                content_type='application/json')
        data = json.loads(response.data.decode())
  
   
   
    def test_user_authenticate_otp_required(self): #TRY WITH NO  DOMAIN FOR A USER WHOSE ORG IS ORG2
        # Valid user create and Validate
        self.external_user_creation_for_test()
        data=json.dumps(dict(
                    username='u3',
                    password='Secret@12' ,
                ))
        with self.client:
            response = self.client.post(
                '/token/gettoken', 
                data=data,
                content_type='application/json')
        data = json.loads(response.data.decode())
        self.assertTrue(data['status'] ==  'Domain_Error')
   
   
    def test_otp_gen_after_auth(self):    ### ######    #OTP GENERATED  AFTER AUTHENTICATION : WORKING
        # Valid user create and Validate
        self.external_user_creation_for_test()
        data=json.dumps(dict(
                    username='u3',
                    password='Secret@12' ,
                    domain='org2'
                ))
        with self.client:
            response = self.client.post(
                '/token/gettoken', 
                data=data,
                content_type='application/json')
        data = json.loads(response.data.decode())
        # print(data)
        user = User.query.filter_by(username='u3').first()
        userotp = user.otp.otp
        self.assertTrue(userotp,not None)
        self.assertTrue(len(userotp), 4)
        self.assertTrue(type(userotp), "<class 'int'>")
        self.assertTrue(data.get('status') == 'OTP_SENT')
   
   
   
    def test_get_token_uname_otp(self):   #########OTP VALIDATION : WORKING 
        self.external_user_creation_for_test()
        data=json.dumps(dict(
                    username='u3',
                    password='Secret@12' ,
                    domain='org2'
                ))
        with self.client:
            response = self.client.post(
                '/token/gettoken', 
                data=data,
                content_type='application/json')
        data = json.loads(response.data.decode())
        user = User.query.filter_by(username='u3').first()        
        userotp = user.otp.otp
        data=json.dumps(dict(
                    username='u3',
                    otp=userotp
                ))
        with self.client:
            response = self.client.post(
                '/token/gettoken', 
                data=data,
                content_type='application/json')
        data = json.loads(response.data.decode())
        self.assertTrue(data['status'] == 'success')
        self.assertTrue('auth_token' in data)
  
  
     
    def test_token_gen_failed_for_unregistered_user(self):   # USER NOT REGISTERED , working
        with self.client:
            response = self.client.post(
                '/token/gettoken',
                data=json.dumps(dict(
                    username='susan',
                    password='mySecret@12',
                    domain='default' )),
                content_type='application/json')
            data = json.loads(response.data.decode())
            self.assertTrue(data['message'] == 'User not registered')
  
  
   
    def test_token_gen_failed_for_unregistered_domain(self):   #unregistered domain : working
        with self.client:
            response = self.client.post(
                '/token/gettoken',
                data=json.dumps(dict(
                    username='susan',
                    password='mySecret@12',
                    domain='torg' )),
                content_type='application/json')
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'DomainConfigurationError')
  
  
  
    def test_invalid_token(self):  #INVALID TOKEN, working
        junk_token = "11eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCJ9.eyJzdWIiOnsiaWQiOjEsInVzZXJuYW1lIjoic3VzYW4iLCJlbWFpbCI6InN1c2FuQGFiYy5jb20ifSwiaWF0IjoxNTQ3ODI0ODcyLCJleHAiOjE1NDc4Mjg0NzJ9.h8w8NzCC7FGGBo1nUrBKHRrYiFI0KrXujLx-GpThOzk8Gqcw-bWAy_jng-EllHJAay7aWw8u6K3B7T62OrZ5Hkj0qKMcwtZPQMySooTSWGW-I1LI3_vKSYhaXjXwayl--Ke3ZPBI1fFN61wUXDJsMuNydlE4eUv60MIAI5eT7o5GjSwfXETT1uv4mO5uHb-Yxf_tU13UMDt8nHX99h2s8WNZarLr3e5lJv786Y6aB4satzKTE3IhQ2HDqhnlRkxT00kRyd-dBeTzpZeA0SiCSUqF6pRbWHEgEGJPr_p-upxBAc_IP_zfUkyygGsRcUNM_lMF5RGLCRSFzeQ4TxBtDQ"
        with self.client:
            self.headers = {'X-Auth-Token': junk_token}
            response = self.client.get(
                '/token/verify_token',                
                headers=self.headers)
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'Invalid token')
            self.assertTrue(isinstance('payload', str))
  
  
  
    def test_token_gen_fail_with_wrong_password(self):   #WORNG PASSWORD working
        u1 = self.user_creation_for_test()
        with self.client:
            response = self.client.post(
                '/token/gettoken',
                data=json.dumps(dict(
                    username='u1',
                    password='wrong_password',
                    domain='org1'
                     )),
                content_type='application/json')
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'AuthenticationFailure')
            self.assertFalse('auth_token' in data)
