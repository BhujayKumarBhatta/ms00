import datetime
import unittest
from flask_testing import TestCase
from flask import Flask
from tokenleader import app1
from tokenleader.app1 import db
from tokenleader.app1.configs import testconf
#from flask_testing import LiveServerTestCase
from tokenleader.app1.authentication.auth_routes import token_login_bp
from tokenleader.app1.adminops.adminops_restapi import adminops_bp
from tokenleader.app1.catalog.catalog_restapi import catalog_bp
from tokenleader.app1.authentication.tokenmanager import TokenManager
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

#from app_run import bp_list
bp_list = [token_login_bp, adminops_bp, catalog_bp ]


# from app_run import app

app = app1.create_app(config_map_list = testconf.test_conf_list,  blue_print_list=bp_list)
#app = app1.create_app(config_map_list = test_configs)

#class BaseTestCase(LiveServerTestCase):
class BaseTestCase(TestCase):
    def create_app(self):       
#         app.config.from_object('app1.configs.testconfigs.TestConfig')
        app.config['TESTING'] = True
        app.config['LIVESERVER_PORT'] = 0
        return app
    
    def setUp(self):
        db.create_all()
        db.session.commit()
    
    def tearDown(self):
        db.session.remove()
        db.drop_all()
    
    def get_auth_token_with_actual_rsa_keys_fake_user(self):         
          
        tm = TokenManager(user_from_db)

        payload = {
                    'exp': (datetime.datetime.utcnow() + \
                            datetime.timedelta(days=0,
                                               seconds=app.config.get('tokenexpiration'))),
                    'iat': datetime.datetime.utcnow(),
                    'sub': user_from_db
                     }
        privkey = app.config.get('private_key')
        publickey = app.config.get('public_key')
#         print(current_app.config.get('token'))
        auth_token = tm.generate_encrypted_auth_token(payload, privkey)#        
        return auth_token       
    
    
        
        
#     def test_get_token(self):
#         with self.client as C:
#             data_dict = {"username": "susan", "password": "mysecret"}
#             data = json.dumps(data_dict)
#             C.post(
#                 '/token/gettoken',
#                 data,
#                 content_type='application/json'
#                 )
#             
        
        
if __name__ =='__main__':
    unittest.main()
    
    