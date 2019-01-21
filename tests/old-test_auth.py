import unittest
import datetime
import json
import jwt
from flask import current_app
from app1.authentication.token_after_login import \
 generate_encrypted_auth_token , decrypt_n_verify_token

from tests.base_test import  BaseTestCase
from app1 import db
from app1.authentication.models import User

#app.app_context().push()


class TestToken(BaseTestCase):
    '''
    (venvp3flask) bhujay@DESKTOP-DTA1VEB:/mnt/c/mydev/myflask$ python -m unittest discover tests
    '''
#       
    def test_auth_token_with_actual_rsa_keys(self):
          
        user_from_db = {
            'id': 1,
            'username': 'susan',
            'email':  'susan@abc.com',            
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
        self.assertEqual(np.get('sub'), payload.get('sub'))
#         print('end of  jwt token function.....................')
#     
#   
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
            self.assertTrue(data['status'] == 'User not registered')
            self.assertFalse('auth_token' in data)
            
    def test_token_gen_n_verify_success_for_registered_user(self):
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
                    password='mysecret' )),
                content_type='application/json')
#             print('response is {}'.format(response))
            data = json.loads(response.data.decode())
            #print(data['message'])
            self.assertTrue(data['status'] == 'success')
            self.assertTrue('auth_token' in data)
            mytoken = data['auth_token']
        with self.client:
            response = self.client.post(
                '/token/verify_token',
                data=json.dumps(dict(
                    auth_token=mytoken,
                    )),
                content_type='application/json')
            #print('response is {}'.format(response))
            data = json.loads(response.data.decode())
            #print(data)
            self.assertTrue(data['status'] == 'Verification Successful')
            self.assertTrue('payload' in data)
            self.assertTrue(data['payload'].get('sub').get('username') == 'susan')
        
            
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
            self.assertTrue(data['status'] == 'Wrong Password')
            self.assertFalse('auth_token' in data)
            

           
        
        