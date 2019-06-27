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

    def test_user_authenticate_external(self):
        # Valid user create and Validate
        self.external_user_creation_for_test()
        data=json.dumps(dict(
                    username='u3',
                    password='secret' ,
                    domain='tsp'
                ))
        #print(data)
#         print(self.client)
        with self.client:
            response = self.client.post(
                '/token/gettoken', 
                data=data,
                content_type='application/json')
        data = json.loads(response.data.decode())
        # print(data)
        userdet = User.query.filter_by(username='u3').first()
        userid = userdet.to_dict()['id']
        print(userid)
        otpdet = Otp.query.filter_by(userid=userid).first()
        otp = otpdet.to_dict()['otp']
        self.assertTrue(otp,not None)
        self.assertTrue(len(otp), 4)
        self.assertTrue(type(otp), "<class 'int'>")
        
        # Calling with invalid Data
        data=json.dumps(dict(
                    username='u3',
                    password='secret1' ,
                ))
        #print(data)
#         print(self.client)
        with self.client:
            response = self.client.post(
                '/token/gettoken', 
                data=data,
                content_type='application/json')
        data = json.loads(response.data.decode())
#         print(data)
        self.assertTrue(data['status'], 'failed')