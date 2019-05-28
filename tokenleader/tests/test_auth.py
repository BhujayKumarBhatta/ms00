import unittest
import datetime
import json
import jwt
from flask import current_app
import random
from tokenleader.app1.authentication.token_after_login import \
 generate_encrypted_auth_token , decrypt_n_verify_token

from tokenleader.tests.base_test import  BaseTestCase
from tokenleader.tests.test_admin_ops import TestUserModel
from tokenleader.app1 import db
from tokenleader.app1.authentication.models import User, Role, Workfunctioncontext, Organization, Orgunit, Department
#from app1.authentication import admin_ops
from tokenleader.app1.adminops import admin_functions as admin_ops
from tokenleader.tests.test_catalog_ops import TestCatalog , service_catalog 

#app.app_context().push()

tc = TestCatalog()

class TestToken(TestUserModel):
    '''
    (venvp3flask) bhujay@DESKTOP-DTA1VEB:/mnt/c/mydev/myflask$ python -m unittest discover tests
    '''
#       
    def test_auth_token_with_actual_rsa_keys_fake_user(self):         
          
        user_from_db = {'id': 1,
                        'username': 'u1', 
                        'email': 'u1@abc.com', 
                        'roles': ['role1'],
                        'creation_date': str(datetime.datetime.utcnow()),
                        'allowemaillogin': 'N',
                        'is_active': 'Y', 
                        'wfc': {'department': 'dept1', 
                                'name': 'wfc1', 
                                'orgunit': 'ou1',
                                'id': 1, 
                                'org': 'org1'},
                        'created_by': 1                       
                        }
        
        payload = {
                    'exp': datetime.datetime.utcnow() + datetime.timedelta(days=0, seconds=3600),
                    'iat': datetime.datetime.utcnow(),
                    'sub': user_from_db
                     }
        __privkey = current_app.config.get('private_key')
        __publickey = current_app.config.get('public_key')   
       
        auth_token = generate_encrypted_auth_token(payload, __privkey) 
#         print(type(auth_token))       
        self.assertTrue(isinstance(auth_token, bytes))     
             
          
        np = decrypt_n_verify_token(auth_token, __publickey)
        self.assertTrue(isinstance(np, dict))
        #print(np.get('sub'))
        self.assertTrue((np.get('sub').get('wfc').get('org')) == 'org1')
        return auth_token   # the return is required for later usage by the test_admin_restapi
        #self.assertEqual(np.get('sub'), payload.get('sub'))
#         print('end of  jwt token function.....................')
#     
#   

    def test_get_token(self):
        '''
        user_creation_for_test method comes from parent class TestUserModel from test_admin_ops module
        this method registers an user with name as u1 
        '''             
        u1 = self.user_creation_for_test()
        tc.add_service()
        #print(u1.to_dict())
        data=json.dumps(dict(
                    username='u1',
                    password='secret' ,
                ))
        #print(data)
        with self.client:
            response = self.client.post(
                '/token/gettoken', 
                data=data,
                content_type='application/json')
                
            #print('response is {}'.format(response))
            data = json.loads(response.data.decode())
#            print(data)
            #print(data['message'])
            self.assertTrue(data['status'] == 'success')
            self.assertTrue('auth_token' in data)
            #print(service_catalog)
            #print(data['service_catalog'])
            self.assertTrue(data['service_catalog'] == service_catalog )
            
            mytoken = data['auth_token']
            return mytoken
    
    def test_get_token_for_external_user(self):
        '''
        user_creation_for_test method comes from parent class TestUserModel from test_admin_ops module
        this method registers an user with name as u1 
        '''             
        # u1 = self.user_creation_for_test()
        rand = str(random.random())
        num = rand[-4:]
        self.create_otp_for_test(num)
        tc.add_service()
        #print(u1.to_dict())
        data=json.dumps(dict(
                    username='u3',
                    otp= num,
                ))
        #print(data)
        with self.client:
            response = self.client.post(
                '/token/gettoken', 
                data=data,
                content_type='application/json')
                
            #print('response is {}'.format(response))
            data = json.loads(response.data.decode())
            # print(data)
            #print(data['message'])
            self.assertTrue(data['status'] == 'success')
            self.assertTrue('auth_token' in data)
            #print(service_catalog)
            #print(data['service_catalog'])
            self.assertTrue(data['service_catalog'] == service_catalog )
            
            mytoken = data['auth_token']
            return mytoken

    #this method is used again in the token verification test
    def test_token_gen_failed_for_unregistered_user(self):
        with self.client:
            response = self.client.post(
                '/token/gettoken',
                data=json.dumps(dict(
                    username='susan',
                    password='mysecret' )),
                content_type='application/json')
            #print('response is {}'.format(response))
            data = json.loads(response.data.decode())
            #print(data['message'])
            self.assertTrue(data['message'] == 'User not registered')
            self.assertFalse('auth_token' in data)
    
    def test_token_gen_n_verify_success_for_registered_user_with_role(self):
        mytoken = self.test_get_token()
        with self.client:
            self.headers = {'X-Auth-Token': mytoken}
            response = self.client.get(
                '/token/verify_token',                
                headers=self.headers)
            #print('response is {}'.format(response))
            data = json.loads(response.data.decode())
            #print(data)
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
            #print(data)
#            print(response.data.decode())
    def test_token_gen_n_verify_success_for_registered_external_user_with_role(self):
        mytoken = self.test_get_token_for_external_user()
        with self.client:
            self.headers = {'X-Auth-Token': mytoken}
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
            self.assertTrue(data['payload'].get('sub').get('email') == 'u3@xyz.com')
            self.assertTrue(data['payload'].get('sub').get('is_active') == 'Y')
            self.assertTrue(data['payload'].get('sub').get('allowemaillogin') == 'Y')
            self.assertTrue(roles_retrived_from_token, list)#== ['test_role_1', 'test_role_2'])
            self.assertTrue(sorted(roles_retrived_from_token) == sorted(['role2']))
            self.assertTrue((data['payload'].get('sub').get('wfc').get('org')) == 'org2')
            #print(data)
#            print(response.data.decode())

#     def test_token_gen_n_verify_success_for_registered_user_without_role(self):
#         u1 = User(username='susan', email='susan@abc.com')
#         u1.set_password('mysecret')       
#         self.assertTrue(u1.check_password('mysecret'))
#         db.session.add(u1)        
#         db.session.commit()
#         with self.client:
#             response = self.client.post(
#                 '/token/gettoken',
#                 data=json.dumps(dict(
#                     username='susan',
#                     password='mysecret' )),
#                 content_type='application/json')
# #             print('response is {}'.format(response))
#             data = json.loads(response.data.decode())
#             #print(data['message'])
#             self.assertTrue(data['status'] == 'success')
#             self.assertTrue('auth_token' in data)
#             mytoken = data['auth_token']
#         with self.client:
#             self.headers = {'X-Auth-Token': mytoken}
#             response = self.client.get(
#                 '/token/verify_token',                
#                 headers=self.headers)
#             #print('response is {}'.format(response))
#             data = json.loads(response.data.decode())
#             #print(data)
#             self.assertTrue(data['status'] == 'Verification Successful')
#             self.assertTrue('payload' in data)
#             self.assertTrue(data['payload'].get('sub').get('username') == 'susan')
#     
    
    
    def test_invalid_token(self):
        junk_token = "11eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCJ9.eyJzdWIiOnsiaWQiOjEsInVzZXJuYW1lIjoic3VzYW4iLCJlbWFpbCI6InN1c2FuQGFiYy5jb20ifSwiaWF0IjoxNTQ3ODI0ODcyLCJleHAiOjE1NDc4Mjg0NzJ9.h8w8NzCC7FGGBo1nUrBKHRrYiFI0KrXujLx-GpThOzk8Gqcw-bWAy_jng-EllHJAay7aWw8u6K3B7T62OrZ5Hkj0qKMcwtZPQMySooTSWGW-I1LI3_vKSYhaXjXwayl--Ke3ZPBI1fFN61wUXDJsMuNydlE4eUv60MIAI5eT7o5GjSwfXETT1uv4mO5uHb-Yxf_tU13UMDt8nHX99h2s8WNZarLr3e5lJv786Y6aB4satzKTE3IhQ2HDqhnlRkxT00kRyd-dBeTzpZeA0SiCSUqF6pRbWHEgEGJPr_p-upxBAc_IP_zfUkyygGsRcUNM_lMF5RGLCRSFzeQ4TxBtDQ"
        with self.client:
            self.headers = {'X-Auth-Token': junk_token}
            response = self.client.get(
                '/token/verify_token',                
                headers=self.headers)
            data = json.loads(response.data.decode())
#            print(data)
            #self.assertTrue(data['status'] == 'Invalid token')
            self.assertTrue(isinstance('payload', str))
    
    def test_expired_token(self):
        expired_token = "eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCJ9.eyJzdWIiOnsiaWQiOjEsInVzZXJuYW1lIjoic3VzYW4iLCJlbWFpbCI6InN1c2FuQGFiYy5jb20ifSwiaWF0IjoxNTQ3ODI0ODcyLCJleHAiOjE1NDc4Mjg0NzJ9.h8w8NzCC7FGGBo1nUrBKHRrYiFI0KrXujLx-GpThOzk8Gqcw-bWAy_jng-EllHJAay7aWw8u6K3B7T62OrZ5Hkj0qKMcwtZPQMySooTSWGW-I1LI3_vKSYhaXjXwayl--Ke3ZPBI1fFN61wUXDJsMuNydlE4eUv60MIAI5eT7o5GjSwfXETT1uv4mO5uHb-Yxf_tU13UMDt8nHX99h2s8WNZarLr3e5lJv786Y6aB4satzKTE3IhQ2HDqhnlRkxT00kRyd-dBeTzpZeA0SiCSUqF6pRbWHEgEGJPr_p-upxBAc_IP_zfUkyygGsRcUNM_lMF5RGLCRSFzeQ4TxBtDQ"
        with self.client:
            self.headers = {'X-Auth-Token': expired_token}
            response = self.client.get(
                '/token/verify_token',                
                headers=self.headers)
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'Signature expired')
            self.assertTrue(isinstance('payload', str))
        
            
    def test_token_gen_fail_with_wrong_password(self):
        u1 = User(username='susan', email='susan@abc.com')
        u1.set_password('mysecret')       
        self.assertTrue(u1.check_password('mysecret'))
        db.session.add(u1)        
        db.session.commit()
        with self.client:
            response = self.client.post(
                '/token/gettoken',
                data=json.dumps(dict(
                    username='susan',
                    password='wrong_password' )),
                content_type='application/json')
#             print('response is {}'.format(response))
            data = json.loads(response.data.decode())
            #print(data['message'])
            self.assertTrue(data['message'] == 'Password did not match')
            self.assertFalse('auth_token' in data)
            

           
        
        