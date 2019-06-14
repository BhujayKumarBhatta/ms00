import unittest
from tokenleader import app1
from tokenleader.app1 import db
from tokenleader.app1.authentication import models
from tokenleader.app1.authentication.models import User, Role, Workfunctioncontext, Organization, Orgunit, Department
from tokenleader.app1.adminops import admin_functions as af
from tokenleader.tests.base_test import  BaseTestCase
from unittest.mock import patch
import random
#app.app_context().push()

class TestUserModel(BaseTestCase):
    '''
    (venvp3flask) bhujay@DESKTOP-DTA1VEB:/mnt/c/mydev/myflask$ python -m unittest discover test
        if we are getting the
        # sqlalchemy.orm.exc.DetachedInstanceError: Instance <Role at 0x7f41a5a4c9e8> is not bound to a Session; attribute refresh operation cannot proceed (Background on this error at: http://sqlalche.me/e/bhk3)
        remove the  block  finally:
#         db.session.close()
         from the api_function
    '''

    def create_otp_for_test(self, num):
        if not User.query.filter_by(username='u3').first():
            self.external_user_creation_for_test()
        else:
            print('u3 was registered before.')
        user = User.query.filter_by(username='u3').first()
        userid = user.to_dict()['id']
        otp = af.create_otp(num, userid)
        return otp

    def test_create_otp(self):
        rand = str(random.random())
        num = rand[-4:]
        otp = self.create_otp_for_test(num)
        self.assertTrue(otp.get('otp'), num)
        
    def create_org_for_test(self):
        return af.register_org('org1')

    def create_external_org_for_test(self):
        return af.register_org('org2', 'external')
    
    def create_orgunit_for_test(self):
        return af.register_ou('ou1')
    
    def create_dept_for_test(self):
        return af.register_dept('dept1')

    def create_external_user_dept_for_test(self):
        return af.register_dept('dept2')
    
    def register_work_function_for_test(self):
        o= self.create_org_for_test()
        ou = self.create_orgunit_for_test()
        dept = self.create_dept_for_test()
        return af.register_work_func_context('wfc1' ,'org1' ,'ou1' ,'dept1')
    
    def register_external_user_work_function_for_test(self):
        o= self.create_external_org_for_test()
        ou = self.create_orgunit_for_test()
        dept = self.create_external_user_dept_for_test()
        return af.register_work_func_context('wfc2' ,'org2' ,'ou1' ,'dept2')

    def role_creation_for_test(self):       
        wfc = self.register_work_function_for_test()
        r = af.register_role('role1')
        return r

    def role_for_external_user_creation_for_test(self):       
        wfc = self.register_external_user_work_function_for_test()
        r = af.register_role('role2')
        return r
    
    def user_creation_for_test(self):
        self.role_creation_for_test()
        roles = ['role1',]        
        u = af.register_user('u1', 'u1@abc.com', 'secret', roles=roles, wfc_name='wfc1')
        return u

    def external_user_creation_for_test(self):
        self.role_for_external_user_creation_for_test()
        roles = ['role2',]        
        u = af.register_user('u3', 'u3@xyz.com', 'secret', roles=roles, wfc_name='wfc2', allowemaillogin='Y')
        return u
       
    def test_register_org(self):
        o = self.create_org_for_test()
        o1 = Organization.query.filter_by(name='org1').first()
        self.assertTrue(o1.name, 'org1')  

    def test_register_external(self):
        o = self.create_external_org_for_test()
        o1 = Organization.query.filter_by(name='org2').first()
        self.assertTrue(o1.name, 'org2')
        self.assertTrue(o1.orgtype, 'external')
    
    def test_register_orgunit(self):
        self.create_orgunit_for_test()        
        ou1 = Orgunit.query.filter_by(name='ou1').first()
        self.assertTrue(ou1.name, 'ou1')
    
    def test_register_dept(self):
        self.create_dept_for_test()
        dept1 = Department.query.filter_by(name='dept1').first()
        self.assertTrue(dept1.name, 'dept1')
    
    def test_register_work_func_context(self):
        self.register_work_function_for_test()
        wfc_db = Workfunctioncontext.query.filter_by(name='wfc1').first()
        self.assertTrue(wfc_db.name, 'wfc1')
        
    def test_role_creation(self):   
#         db.session.rollback()     
        self.role_creation_for_test()
        rdb = Role.query.filter_by(rolename='role1').first()
        self.assertTrue(rdb.rolename, 'role1')
        
    def test_register_user(self):
        u = self.user_creation_for_test()
        #print(type(u))
        rdb = User.query.filter_by(username='u1').first()
        self.assertTrue(rdb.username, 'u1')
        self.assertTrue(rdb.roles, ['role1',]  )
        
    def test_list_org(self):
        self.create_org_for_test()
        af.list_org()
        
    def test_list_ou(self):
        self.create_orgunit_for_test()
        af.list_ou()
    
    def test_list_dept(self):
        self.create_dept_for_test()
        af.list_dept()
    
    def test_list_dept_single_item(self):
        self.create_dept_for_test()
        af.list_dept('dept1')
        
    def test_list_dept_non_existing(self):        
        af.list_dept('dept_non_existing')
    
    def test_list_wfc(self):
        self.register_work_function_for_test()
        af.list_wfc('wfc1')
    
    def test_list_role(self):
        self.role_creation_for_test()
        af.list_role()
        
    def test_list_users(self):
        self.user_creation_for_test()
        af.list_users()
    
#     @patch('tokenleader.app1.adminops.base_ops.get_input', return_value='yes')
    def test_delete_org(self):
        self.create_org_for_test()
        status = af.delete_org('org1')
        #print(status)
        self.assertTrue(status == "org1 has been  deleted successfully" )

    def test_delete_org_for_external_user(self):
        self.create_external_org_for_test()
        status = af.delete_org('org2')
        #print(status)
        self.assertTrue(status == "org2 has been  deleted successfully" )   
    
#     @patch('tokenleader.app1.adminops.base_ops.get_input', return_value='yes')
    def test_delete_ou(self):
        self.create_orgunit_for_test()
        status = af.delete_ou('ou1')
        #print(status)
        self.assertTrue(status == "ou1 has been  deleted successfully" )
        
#     @patch('tokenleader.app1.adminops.base_ops.get_input', return_value='yes')
    def test_delete_dept(self):
        self.create_dept_for_test()
        status = af.delete_dept('dept1')
        #print(status)
        self.assertTrue(status == "dept1 has been  deleted successfully" )

    def test_delete_dept_for_external_user(self):
        self.create_external_user_dept_for_test()
        status = af.delete_dept('dept2')
        #print(status)
        self.assertTrue(status == "dept2 has been  deleted successfully" )
    
#     @patch('tokenleader.app1.adminops.base_ops.get_input', return_value='yes')
    def test_delete_wfc(self):
        self.register_work_function_for_test()
        status = af.delete_wfc('wfc1')      
        self.assertTrue(status == "wfc1 has been  deleted successfully" )

    def test_delete_wfc_for_external_user(self):
        self.register_external_user_work_function_for_test()
        status = af.delete_wfc('wfc2')      
        self.assertTrue(status == "wfc2 has been  deleted successfully" )
        
#     @patch('tokenleader.app1.adminops.base_ops.get_input', return_value='yes')
    def test_delete_role(self):
        self.role_creation_for_test()
        status = af.delete_role('role1')      
        self.assertTrue(status == "role1 has been  deleted successfully" )

    def test_delete_role_external_user(self):
        self.role_for_external_user_creation_for_test()
        status = af.delete_role('role2')      
        self.assertTrue(status == "role2 has been  deleted successfully" )        
   
#     @patch('tokenleader.app1.adminops.base_ops.get_input', return_value='yes')
    def test_delete_user(self):
        self.user_creation_for_test()
        status = af.delete_user('u1')      
        self.assertTrue(status == "u1 has been  deleted successfully" )

    def test_delete_external_user(self):
        self.external_user_creation_for_test()
        status = af.delete_user('u3')      
        self.assertTrue(status == "u3 has been  deleted successfully" )





    
    
