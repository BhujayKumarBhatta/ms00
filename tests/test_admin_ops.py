import unittest
from unittest.mock import patch
from tests.base_test import  BaseTestCase
from app1.authentication import admin_ops
from app1.authentication.models import User, Role
from collections.abc import Iterable
from app1 import db

#app.app_context().push()

class TestAdminOps(BaseTestCase):
    '''
    (venvp3flask) bhujay@DESKTOP-DTA1VEB:/mnt/c/mydev/myflask$ python -m unittest discover tests
    '''
    ####################Role Related testing###########################################
    def test_register_role(self):
        admin_ops.register_role('test_role')
        r1 = Role.query.filter_by(rolename='test_role').first()
        self.assertEqual(r1.rolename, 'test_role')
        self.assertTrue(isinstance(r1.id, int))
        
    def test_duplicate_register_role(self):
        r1 = Role(rolename='test_role')
        db.session.add(r1)
        db.session.commit()
        result = admin_ops.register_role('test_role')
        self.assertEqual(result,
                         'databse integrity error, role by the same name may be already present')        
        
    def test_list_role(self):
        admin_ops.register_role('test_role')
        r = Role.query.filter_by(rolename='test_role').first()
        o = admin_ops.list_roles('test_role')
        #print(l)
        self.assertEqual(r, o)
        l = admin_ops.list_roles()
        self.assertTrue(l, Iterable)
    
    def test_delete_nonexisting_role(self):        
        status = admin_ops.delete_role('nonexistingrole')
        self.assertTrue(status, 'Role  not found in database') 
    
    @patch('app1.authentication.admin_ops.get_input', return_value='yes')
    def test_delete_role_confirmation_yes(self, input):
        admin_ops.register_role('test_role')
        status = admin_ops.delete_role('test_role')
        self.assertTrue(status, "Role:  test_role has been  deleted sucessfully")
        
    @patch('app1.authentication.admin_ops.get_input', return_value='no')
    def test_abort_delete_role_input_not_yes(self, input):
        admin_ops.register_role('test_role')
        status = admin_ops.delete_role('test_role')
        self.assertTrue(status, "Aborting deletion")     
        
        
    ###################### User related testings #########################################
    ##          USER Operation testing  with relationship to role table
    ##########################################################################################
    def test_register_admin_user(self):
        admin_ops.register_admin_user('susan', 'susan@itc.in', 'mysecret', 'admin')
        u1 = User.query.filter_by(username='susan').first()
        self.assertTrue(u1.check_password('mysecret'))
        self.assertTrue(u1.email, 'susan@itc.in')
        self.assertTrue(u1.role, 'admin')
        
    def test_duplicate_register_admin_user(self):
        u1 = User(username='test_duplicate_user', email='test_duplicate_user@test.com')
        db.session.add(u1)
        db.session.commit()
        result = admin_ops.register_admin_user('test_duplicate_user', 'test_duplicate_user@test.com',
                                           'mysecret', 'admin' )
        self.assertEqual(result,
                         'databse integrity error, username or email address is already present')  
        
    def test_list_admin_users(self):
        admin_ops.register_admin_user('susan', 'susan@itc.in', 'mysecret', 'admin')
#         admin_ops.register_admin_user('susan3', 'susan3@itc.in', 'mysecret', 'admin')
#         u1 = User(username='uname11', email='email11', role='admin')
#         u1.set_password('pwd')     
#         try:
#             db.session.add(u1)        
#             db.session.commit()
#             print("admin user has been  registered sucessfully")
#         except  Exception as e:
#             print("user  could not be registered , the erro is: \n  {}".format(e))
        r = admin_ops.list_admin_users('all')
#         print(type(r))
#         self.assertTrue(isinstance(r, Iterable ))
#         r1 = admin_ops.list_admin_users('susan')
#         self.assertTrue(r1.username, 'susan')
        
        
    def test_delete_nonexisting_admin_user(self):        
        status = admin_ops.delete_admin_user('nonexisting', 'email', 'admin')
        self.assertTrue(status, 'User  not found in database')
    
    @patch('app1.authentication.admin_ops.get_input', return_value='yes')
    def test_delete_admin_user_confirmation_yes(self, input):
        admin_ops.register_admin_user('susan', 'susan@itc.in', 'mysecret', 'admin')
        status = admin_ops.delete_admin_user('susan', 'susan@itc.in' 'admin')
        self.assertTrue(status, " User susan has been  deleted sucessfully")
        
    @patch('app1.authentication.admin_ops.get_input', return_value='no')
    def test_abort_delete_admin_user_input_not_yes(self, input):
        admin_ops.register_admin_user('susan', 'susan@itc.in', 'mysecret', 'admin')
        status = admin_ops.delete_admin_user('susan', 'susan@itc.in' 'admin')
        self.assertTrue(status, "Aborting deletion")
        
    
    