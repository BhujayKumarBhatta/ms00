import unittest
from unittest.mock import patch
from tests.base_test import  BaseTestCase
from app1.authentication import admin_ops
from app1.authentication.models import User, Role
from collections.abc import Iterable
from app1 import db

#app.app_context().push()

class TestUserOps(BaseTestCase):
    '''
    (venvp3flask) bhujay@DESKTOP-DTA1VEB:/mnt/c/mydev/myflask$ python -m unittest discover tests
    '''
            
    ###################### User related testings #########################################
    ##          USER Operation testing  with relationship to role table
    ##########################################################################################
    def test_register_user_without_roles(self):
        admin_ops.register_user('susan', 'susan@itc.in', 'mysecret')
        u1 = User.query.filter_by(username='susan').first()
        self.assertTrue(u1.check_password('mysecret'))
        self.assertTrue(u1.email, 'susan@itc.in')
        
        
    def test_duplicate_register_user(self):
        u1 = User(username='test_duplicate_user', email='test_duplicate_user@test.com')
        db.session.add(u1)
        db.session.commit()
        result = admin_ops.register_user('test_duplicate_user', 'test_duplicate_user@test.com',
                                           'mysecret')
        self.assertEqual(result,
                         'databse integrity error, username or email address is already present')  
        
    def test_register_user_with_roles(self):
        r1 = Role(rolename='test_role_1')
        r2 = Role(rolename='test_role_2')
        db.session.add(r1)
        db.session.add(r2)
        db.session.commit()
        
        input_roles = ['test_role_1',
                       'test_role_2',
                       'test_role_3',
                       'test_role_4',]
         
        admin_ops.register_user('susan', 'susan@itc.in', 'mysecret', input_roles)
        u1 = User.query.filter_by(username='susan').first()
        for r in u1.roles:            
                self.assertTrue(r.rolename in input_roles)       
        
        
    def test_list_users(self):
        r1 = Role(rolename='test_role_1')
        r2 = Role(rolename='test_role_2')
        db.session.add(r1)
        db.session.add(r2)
        db.session.commit()    
        input_roles = ['test_role_1',
                       'test_role_2',
                       'test_role_3',
                       'test_role_4',]
        
        admin_ops.register_user('user_1', 'user_1@itc.in', 'mysecret', input_roles)
        #admin_ops.register_user('user_30', 'user_30@itc.in', 'mysecret')#   
        u1 = User.query.filter_by(username='user_1').first() # Why  without this line
        # list_admin_user is not showing the whole list ?????????????????????????????????
#         for r in u1.roles:
#             print(r.rolename)    
        admin_ops.list_admin_users('user_1')
        
        
        
        
    def test_delete_nonexisting_admin_user(self):        
        status = admin_ops.delete_admin_user('nonexisting', 'email', 'admin')
        self.assertTrue(status, 'User  not found in database')
    
    @patch('app1.authentication.admin_ops.get_input', return_value='yes')
    def test_delete_admin_user_confirmation_yes(self, input):
        admin_ops.register_user('susan', 'susan@itc.in', 'mysecret')
        status = admin_ops.delete_admin_user('susan', 'susan@itc.in')
        self.assertTrue(status, " User susan has been  deleted sucessfully")
        
    @patch('app1.authentication.admin_ops.get_input', return_value='no')
    def test_abort_delete_admin_user_input_not_yes(self, input):
        admin_ops.register_user('susan', 'susan@itc.in', 'mysecret')
        status = admin_ops.delete_admin_user('susan', 'susan@itc.in')
        self.assertTrue(status, "Aborting deletion")
        
    
    