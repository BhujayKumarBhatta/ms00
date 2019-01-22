import unittest
from unittest.mock import patch
from tests.base_test import  BaseTestCase
from app1.authentication import admin_ops
from app1.authentication.models import User
from collections.abc import Iterable


#app.app_context().push()

class TestAdminOps(BaseTestCase):
    '''
    (venvp3flask) bhujay@DESKTOP-DTA1VEB:/mnt/c/mydev/myflask$ python -m unittest discover tests
    '''
    
    def test_register_admin_user(self):
        admin_ops.register_admin_user('susan', 'susan@itc.in', 'mysecret', 'admin')
        u1 = User.query.filter_by(username='susan').first()
        self.assertTrue(u1.check_password('mysecret'))
        self.assertTrue(u1.email, 'susan@itc.in')
        self.assertTrue(u1.role, 'admin')
        
    def test_list_admin_users(self):
        admin_ops.register_admin_user('susan', 'susan@itc.in', 'mysecret', 'admin')
        admin_ops.register_admin_user('susan3', 'susan3@itc.in', 'mysecret', 'admin')
        r = admin_ops.list_admin_users('all')
#         print(type(r))
        self.assertTrue(isinstance(r, Iterable ))
        r1 = admin_ops.list_admin_users('susan')
        self.assertTrue(r1.username, 'susan')
        
        
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
        
    
    