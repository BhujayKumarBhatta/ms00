import unittest
from flask_testing import TestCase
from flask import Flask
from  tokenleader import app1
from tokenleader.app1 import db
from tokenleader.app1.configs.configs import test_configs
import json
from flask_testing import LiveServerTestCase


from tokenleader.app1.authentication.token_after_login import token_login_bp
from tokenleader.app1.adminops.adminops_restapi import adminops_bp
#from app_run import bp_list
bp_list = [token_login_bp, adminops_bp]


# from app_run import app

app = app1.create_app(config_map_list = test_configs,  blue_print_list=bp_list)
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
    
    def test_configs(self):
        #self.assertTrue(app.config['DEBUG'] is True)
        #self.assertTrue(app.config['SQLALCHEMY_DATABASE_URI'] == 'sqlite:////tmp/test_auth.db')
        self.assertTrue(app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] is False)
        self.assertIsNotNone(app.config['private_key'])
        self.assertIsNotNone(app.config['public_key'])
        
        
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
    
    