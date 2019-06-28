''' test configd'''
import os
from unittest import TestCase
from tokenleader.app1.configs.testconf import conf as testconf
from flask import current_app
from tokenleader.tests.base_test import app

test_data_path = os.path.join(os.path.dirname(__file__), 'testdata')
test_secret_file= os.path.join(test_data_path,'secrets.yml')

# conf_file='tokenleader/tests/testdata/test_tokenleader_configs.yml'
# must_have_keys_in_yml = {'host_name',
#                              'host_port',
#                              'ssl',
#                              'ssl_settings',
#                              'database',
#                              'secrets'
#                              'celery'
#                              }
must_have_keys_in_yml = {}
# conf = Configs('tokenleader', conf_file=conf_file, must_have_keys_in_yml=must_have_keys_in_yml)
# yml = conf.yml

class  TestConf(TestCase):
    
    def test_configs(self):
        #self.assertTrue(app.config['DEBUG'] is True)
        #self.assertTrue(app.config['SQLALCHEMY_DATABASE_URI'] == 'sqlite:////tmp/test_auth.db')
        self.assertTrue(app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] is False)
        self.assertIsNotNone(app.config['private_key'])
        self.assertIsNotNone(app.config['public_key'])
        self.assertIsNotNone(app.config['token'])
        self.assertTrue(app.config.get('token').get('tokenexpiration') == 2)
    
    def test_simple_conf(self):        
        #conf = Configs('tokenleader', conf_file=SERVER_SETTINGS_FILE, must_have_keys_in_yml=must_have_keys_in_yml)
        c = testconf.yml
        self.assertTrue(c.get('flask_default').get('host_name') == '0.0.0.0')
        print(c.get('celery'))        
        #print(current_app.configs)
        
    def test_encrypt_conf(self):
        #conf = Configs('tokenleader', conf_file=SERVER_SETTINGS_FILE)
        c = testconf.yml
        testconf.generate_secret_file('db_pwd', 'welcome@123' )
        secret_yml = testconf.parse_yml(test_secret_file)
        pwd1 = secret_yml.get('db_pwd')
        testconf.generate_secret_file('db_pwd', 'welcome@123')
        secret_yml = testconf.parse_yml(test_secret_file)
        pwd2 = secret_yml.get('db_pwd')
#         print(pwd1+"\n\n"+pwd2)
        self.assertFalse(pwd1 == pwd2)
#         self.assertTrue(secret_yml['existing_data'] == "reatiened well")
        
    def test_decrypt(self):
        #conf = Configs('tokenleader', conf_file=SERVER_SETTINGS_FILE)
        c = testconf.yml
        testconf.generate_secret_file('db_pwd', 'welcome@123' )
        secret_yml = testconf.parse_yml(test_secret_file)
        pwd1 = secret_yml.get('db_pwd')
        p = testconf.decrypt_password('db_pwd')
        self.assertTrue(p == 'welcome@123')

        