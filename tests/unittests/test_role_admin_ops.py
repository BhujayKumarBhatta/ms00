import unittest
from unittest.mock import patch
from tests.base_test import  BaseTestCase
from app1.authentication import admin_ops
from app1.authentication.models import  Role
from collections.abc import Iterable
from app1 import db

#app.app_context().push()

class TestRoleOps(BaseTestCase):
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
        

    def test_get_validated_roles(self):
        r1 = Role(rolename='test_role_1')
        r2 = Role(rolename='test_role_2')
        db.session.add(r1)
        db.session.add(r2)
        db.session.commit()
        roles_to_be_tested = ['test_role_1',
                              'test_role_2',
                              'test_role_3',
                              'test_role_4',]              
        result = admin_ops.get_validated_roles(roles_to_be_tested)          
        self.assertEqual(result, [r1,r2] )
        #self.assertEqual(sorted(result), invalid_role_input )
        
        