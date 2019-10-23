from tokenleader.app1.authentication.models import User
from tokenleader.app1.adminops import admin_functions as af
from tokenleader.tests.base_test import  BaseTestCase
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

    
    def create_default_org_for_test(self):
        return af.register_org('default')
    
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
    
    def register_default_work_function_for_test(self):
        self.create_default_org_for_test()
        self.create_orgunit_for_test()
        self.create_dept_for_test()
        return af.register_work_func_context('wfc_default' ,'default' ,'ou1' ,'dept1')
    
    def register_external_user_work_function_for_test(self):
        o= self.create_external_org_for_test()
        ou = self.create_orgunit_for_test()
        dept = self.create_external_user_dept_for_test()
        return af.register_work_func_context('wfc2' ,'org2' ,'ou1' ,'dept2')

    def role_creation_for_test(self):       
        wfc = self.register_work_function_for_test()
        r = af.register_role('role1')
        return r
    
    def role_default_user_creation_for_test(self):       
        self.register_default_work_function_for_test()
        r = af.register_role('default_role')
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
        u = af.register_user('u3', 'Srijib.Bhattacharyya@itc.in', 'secret', 
                             otp_mode='mail',
                             roles=roles,  
                             wfc_name='wfc2', allowemaillogin='Y')
        return u
    
    def user_default_domain_creation_for_test(self):
        self.role_default_user_creation_for_test()
        roles = ['default_role',]        
        u = af.register_user('user_default_domain', 'user_default_domain@itc.in', 'secret', 
                             otp_mode='mail',
                             roles=roles,
                             wfc_name='wfc_default', allowemaillogin='Y')
        return u
