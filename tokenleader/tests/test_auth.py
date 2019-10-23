import time
import datetime
import json
from flask import current_app
import random
from tokenleader.app1.authentication.tokenmanager import TokenManager
from tokenleader.app1.authentication.authenticator import Authenticator
from tokenleader.tests.admin_ops import TestUserModel
# from tokenleader.app1 import db
from tokenleader.app1.authentication.models import User, Role, Workfunctioncontext, Organization, Orgunit, Department, Otp
from tokenleader.app1.adminops import admin_functions as af
from tokenleader.tests.test_catalog_ops import TestCatalog , service_catalog
tc = TestCatalog()
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
                                'org': 'default'},
                        'created_by': 1
                        }


class TestToken(TestUserModel):
    '''
    (venvp3flask) bhujay@DESKTOP-DTA1VEB:/mnt/c/mydev/myflask$ python -m unittest discover tests
    '''
    EMAIL_TEST='Srijib.Bhattacharyya@itc.in'
  
    
#       
#     def test_auth_token_with_actual_rsa_keys_fake_user(self):         
#         tm = TokenManager(user_from_db)
#         #current_app.config.get('tokenexpiration')
#         payload = {
#                     'exp': (datetime.datetime.utcnow() + \
#                             datetime.timedelta(days=0,
#                                                seconds=3600)),
#                     'iat': datetime.datetime.utcnow(),
#                     'sub': user_from_db
#                      }
#         privkey = current_app.config.get('private_key')
#         publickey = current_app.config.get('public_key')
#         auth_token = tm.generate_encrypted_auth_token(payload, privkey)
#         self.assertTrue(isinstance(auth_token, bytes))
#         np = tm.decrypt_n_verify_token(auth_token, publickey)
#         self.assertTrue(isinstance(np, dict))
#         self.assertTrue((np.get('payload').get('sub').get('wfc').get('org')) == 'default')
#         return auth_token   # the return is required for later usage by the test_admin_restapi
#         #self.assertEqual(np.get('sub'), payload.get('sub'))
# #         print('end of  jwt token function.....................')
# #     
# #   
#    

#     def test_get_token(self):   #working
#         '''
#         user_creation_for_test method comes from parent class TestUserModel from test_admin_ops module
#         this method registers an user with name as u1 
#         '''
#         u1 = self.user_creation_for_test()
#         tc.add_service()#print(u1.to_dict())
#         data=json.dumps(dict(
#                     username='u1',
#                     password='secret' ,
#                     domain='org1'
#                 ))
#         with self.client:
#             response = self.client.post(
#                 '/token/gettoken', 
#                 data=data,
#                 content_type='application/json')
#             data = json.loads(response.data.decode())
#             self.assertTrue(data['status'] == 'success')
#             self.assertTrue('auth_token' in data)
#             self.assertTrue(data['service_catalog'] == service_catalog )
#             mytoken = data['auth_token']
#             return mytoken


	# CALLING WITH NO DOMAIN WHILE USERS HAS BEEN REGISTERED WITH DEFAULT DOMAIN: working
#     def test_get_token_default_domain(self):   # working
#         self.user_default_domain_creation_for_test()
#         data=json.dumps(dict(
#                     username='user_default_domain',
#                     password='secret' ,
#                 ))
#         with self.client:
#             response = self.client.post(
#                 '/token/gettoken', 
#                 data=data,
#                 content_type='application/json')
#         data = json.loads(response.data.decode())
#         print(data)


#     #OTP GENERATED  AFTER AUTHENTICATION : working
#     def test_user_authenticate_otp_required(self):    #working
#         # Valid user create and Validate
#         self.external_user_creation_for_test()
#         data=json.dumps(dict(
#                     username='u3',
#                     password='secret' ,
#                     domain='org2'
#                 ))
#         with self.client:
#             response = self.client.post(
#                 '/token/gettoken', 
#                 data=data,
#                 content_type='application/json')
#         data = json.loads(response.data.decode())
#         # print(data)
#         user = User.query.filter_by(username='u3').first()
#         userotp = user.otp.otp
#         self.assertTrue(userotp,not None)
#         self.assertTrue(len(userotp), 4)
#         self.assertTrue(type(userotp), "<class 'int'>")
#         self.assertTrue(data.get('status') == 'OTP_SENT')
# 
#         # Calling with no domain while users org is org2, it should try with default domain and fail
#         data=json.dumps(dict(
#                     username='u3',
#                     password='secret' ,
#                 ))
#         with self.client:
#             response = self.client.post(
#                 '/token/gettoken', 
#                 data=data,
#                 content_type='application/json')
#         data = json.loads(response.data.decode())
#         self.assertTrue(data['status'] ==  'Domain_Error')
        
       
#     #OTP VALIDATION : working   
    def test_get_token_uname_otp(self):   #working
        self.external_user_creation_for_test()
        data=json.dumps(dict(
                    username='u3',
                    password='secret' ,
                    domain='org2'
                ))
        with self.client:
            response = self.client.post(
                '/token/gettoken', 
                data=data,
                content_type='application/json')
        data = json.loads(response.data.decode())
        user = User.query.filter_by(username='u3').first()
        userid = user.to_dict()['id']
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
#         
#     def test_get_token_email_otp(self):   #working
#         self.external_user_creation_for_test()
#         data=json.dumps(dict(
#                     username='u3',
#                     password='secret' ,
#                     domain='tsp'
#                 ))
#         with self.client:
#             response = self.client.post(
#                 '/token/gettoken', 
#                 data=data,
#                 content_type='application/json')
#         data = json.loads(response.data.decode())
#         userdet = User.query.filter_by(username='u3').first()
#         userid = userdet.to_dict()['id']
#         otpdet = Otp.query.filter_by(userid=userid).first()
#         otp = otpdet.to_dict()['otp']
#         data=json.dumps(dict(
#                     email=self.EMAIL_TEST,
#                     otp=otp
#                 ))
#         with self.client:
#             response = self.client.post(
#                 '/token/gettoken', 
#                 data=data,
#                 content_type='application/json')
#         data = json.loads(response.data.decode())
#         self.assertTrue(data['status'] == 'success')
#         self.assertTrue('auth_token' in data)
#         
#     def test_get_token_for_external_user(self):
#         '''
#         user_creation_for_test method comes from parent class TestUserModel from test_admin_ops module
#         this method registers an user with name as u3
#         '''
#         # u1 = self.user_creation_for_test()
#         self.external_user_creation_for_test()
#         user = User.query.filter_by(username='u3').first()
#         userid = user.to_dict()['id']
#         rand = str(random.random())
#         num = rand[-4:]
#         otpdet=af.create_otp(num, userid)
#         otpdet['creation_date'] = str(otpdet['creation_date'])
#         tc.add_service()
#         #print(u1.to_dict())
# #        data=json.dumps(dict(
# #                    username='u3',
# #                    otp= num,
# #                ))
#         user_from_db = {'id': 3,
#                         'username': 'u3',
#                         'email': 'u3@xyz.com',
#                         'roles': ['role2'],
#                         'creation_date': str(datetime.datetime.utcnow()),
#                         'allowemaillogin': 'Y',
#                         'is_active': 'Y',
#                         'wfc': {'department': 'dept2',
#                                 'name': 'wfc2',
#                                 'orgunit': 'ou1',
#                                 'id': 2,
#                                 'org': 'org2'},
#                         'created_by': 1
#                         }
#         tm = TokenManager(user_from_db)
# 
#         payload = {
#                     'exp': datetime.datetime.utcnow() + datetime.timedelta(days=0, seconds=3600),
#                     'iat': datetime.datetime.utcnow(),
#                     'sub': {**user_from_db, **otpdet}
#                      }
#         __privkey = current_app.config.get('private_key')
#         __publickey = current_app.config.get('public_key')
#         auth_token = tm.generate_encrypted_auth_token(payload, __privkey)
#         # print(type(auth_token))
#         self.assertTrue(isinstance(auth_token, bytes))
#         np = tm.decrypt_n_verify_token(auth_token, __publickey)
#         self.assertTrue((np.get('sub').get('wfc').get('org')) == 'org2')
#         self.assertTrue(isinstance(np, dict))
#         return auth_token
# 
#     #this method is used again in the token verification test
#     def test_token_gen_failed_for_unregistered_user(self):   #working
#         with self.client:
#             response = self.client.post(
#                 '/token/gettoken',
#                 data=json.dumps(dict(
#                     username='susan',
#                     password='mysecret',
#                     domain='default' )),
#                 content_type='application/json')
#             #print('response is {}'.format(response))
#             data = json.loads(response.data.decode())
#             # print(data)
#             self.assertTrue(data['message'] == 'User not registered')
#             
#     def test_token_gen_failed_for_unregistered_domain(self):   #working
#         with self.client:
#             response = self.client.post(
#                 '/token/gettoken',
#                 data=json.dumps(dict(
#                     username='susan',
#                     password='mysecret',
#                     domain='torg' )),
#                 content_type='application/json')
#             #print('response is {}'.format(response))
#             data = json.loads(response.data.decode())
# #             print(data)
#             self.assertTrue(data['message'] == 'torg domain has not been configured in  tokenleader_configs by administrator')
#     
#     def test_token_gen_n_verify_success_for_registered_user_with_role(self):
#         mytoken = self.test_get_token()
#         with self.client:
#             self.headers = {'X-Auth-Token': mytoken}
#             response = self.client.get(
#                 '/token/verify_token',                
#                 headers=self.headers)
#             #print('response is {}'.format(response))
#             data = json.loads(response.data.decode())
#             # print(data)
#             self.assertTrue(data['status'] == 'Verification Successful')
#             self.assertTrue('payload' in data)
#             roles_retrived_from_token = data['payload'].get('sub').get('roles')
#             self.assertTrue(data['payload'].get('sub').get('username') == 'u1')
#             self.assertTrue(data['payload'].get('sub').get('email') == 'u1@abc.com')
#             self.assertTrue(data['payload'].get('sub').get('is_active') == 'Y')
#             self.assertTrue(data['payload'].get('sub').get('allowemaillogin') == 'N')
#             self.assertTrue(roles_retrived_from_token, list)#== ['test_role_1', 'test_role_2'])
#             self.assertTrue(sorted(roles_retrived_from_token) == sorted(['role1']))
#             self.assertTrue((data['payload'].get('sub').get('wfc').get('org')) == 'org1')
#             #print(data)
# #            print(response.data.decode())
#     def test_token_gen_n_verify_success_for_registered_external_user_with_role(self):
#         mytoken = self.test_get_token_for_external_user()
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
#             roles_retrived_from_token = data['payload'].get('sub').get('roles')
#             self.assertTrue(data['payload'].get('sub').get('username') == 'u3')
#             self.assertTrue(data['payload'].get('sub').get('email') == 'u3@xyz.com')
#             self.assertTrue(data['payload'].get('sub').get('is_active') == 'Y')
#             self.assertTrue(data['payload'].get('sub').get('allowemaillogin') == 'Y')
#             self.assertTrue(roles_retrived_from_token, list)#== ['test_role_1', 'test_role_2'])
#             self.assertTrue(sorted(roles_retrived_from_token) == sorted(['role2']))
#             self.assertTrue((data['payload'].get('sub').get('wfc').get('org')) == 'org2')
#             #print(data)
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
    
    
#     def test_invalid_token(self):
#         junk_token = "11eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCJ9.eyJzdWIiOnsiaWQiOjEsInVzZXJuYW1lIjoic3VzYW4iLCJlbWFpbCI6InN1c2FuQGFiYy5jb20ifSwiaWF0IjoxNTQ3ODI0ODcyLCJleHAiOjE1NDc4Mjg0NzJ9.h8w8NzCC7FGGBo1nUrBKHRrYiFI0KrXujLx-GpThOzk8Gqcw-bWAy_jng-EllHJAay7aWw8u6K3B7T62OrZ5Hkj0qKMcwtZPQMySooTSWGW-I1LI3_vKSYhaXjXwayl--Ke3ZPBI1fFN61wUXDJsMuNydlE4eUv60MIAI5eT7o5GjSwfXETT1uv4mO5uHb-Yxf_tU13UMDt8nHX99h2s8WNZarLr3e5lJv786Y6aB4satzKTE3IhQ2HDqhnlRkxT00kRyd-dBeTzpZeA0SiCSUqF6pRbWHEgEGJPr_p-upxBAc_IP_zfUkyygGsRcUNM_lMF5RGLCRSFzeQ4TxBtDQ"
#         with self.client:
#             self.headers = {'X-Auth-Token': junk_token}
#             response = self.client.get(
#                 '/token/verify_token',                
#                 headers=self.headers)
#             data = json.loads(response.data.decode())
# #            print(data)
#             #self.assertTrue(data['status'] == 'Invalid token')
#             self.assertTrue(isinstance('payload', str))
# 
#     def test_expired_token(self):
#         mytoken = self.test_auth_token_with_actual_rsa_keys_fake_user()
#         time.sleep(10)
#         with self.client:
#             self.headers = {'X-Auth-Token': mytoken}
#             response = self.client.get(
#                 '/token/verify_token',                
#                 headers=self.headers)
#             data = json.loads(response.data.decode())
#             self.assertTrue(data['status'] == 'Signature expired')
#             self.assertTrue(isinstance('payload', str))
# 
# 
#     def test_token_gen_fail_with_wrong_password(self):   #working
#         u1 = self.user_creation_for_test()
#         with self.client:
#             response = self.client.post(
#                 '/token/gettoken',
#                 data=json.dumps(dict(
#                     username='u1',
#                     password='wrong_password',
#                     domain='default'
#                      )),
#                 content_type='application/json')
# #             print('response is {}'.format(response))
#             data = json.loads(response.data.decode())
#             print(data)
#             # print(data['message'])
#             self.assertTrue(data['message'] == 'Authentication Failure')
#             self.assertFalse('auth_token' in data)
