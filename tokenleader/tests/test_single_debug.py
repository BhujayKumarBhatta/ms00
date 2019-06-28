import time
import unittest
import datetime
import json
import jwt
from flask import current_app
import random
from tokenleader.app1.authentication.authclass import TokenManager
from tokenleader.tests.base_test import  BaseTestCase
from tokenleader.tests.test_admin_ops import TestUserModel
from tokenleader.app1 import db
from tokenleader.app1.authentication.models import User, Role, Workfunctioncontext, Organization, Orgunit, Department, Otp
#from app1.authentication import admin_ops
from tokenleader.app1.adminops import admin_functions as af
from tokenleader.tests.test_catalog_ops import TestCatalog , service_catalog 



class TestToken(TestUserModel):
    '''
    (venvp3flask) bhujay@DESKTOP-DTA1VEB:/mnt/c/mydev/myflask$ python -m unittest discover tests
    '''
    EMAIL_TEST='Srijib.Bhattacharyya@itc.in'

    def test_token_gen_failed_for_unregistered_domain(self):   #working
        with self.client:
            response = self.client.post(
                '/token/gettoken',
                data=json.dumps(dict(
                    username='susan',
                    password='mysecret',
                    domain='torg' )),
                content_type='application/json')
            #print('response is {}'.format(response))
            data = json.loads(response.data.decode())
#             print(data)
            self.assertTrue(data['message'] == 'torg domain has not been configured in  tokenleader_configs by administrator')