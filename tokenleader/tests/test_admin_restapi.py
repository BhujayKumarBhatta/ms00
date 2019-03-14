import json
from tokenleader.tests.base_test import  BaseTestCase
from tokenleader.tests.test_admin_ops import TestUserModel
from tokenleader.tests.test_auth import TestToken
test_token_instance = TestToken()
t = TestUserModel()

class TestAdminRestApi(BaseTestCase):
    
    def test_list_users_without_token(self):
        u1 = t.user_creation_for_test()        
        with self.client:
            response = self.client.get('/list/users')
#             print('response is {}'.format(response))
            data = json.loads(response.data.decode())
            #print(data)
            txt = 'this endpoint is restricted , authenticaton or authorization failed'
            self.assertTrue(txt in  data['message'] )
            
    def test_list_users_with_token(self):
        u1 = t.user_creation_for_test()
        token_in_byte = test_token_instance.test_auth_token_with_actual_rsa_keys_fake_user()
        #print(token_in_byte)
        with self.client:
            self.headers = {'X-Auth-Token': token_in_byte}
            response = self.client.get(
                '/list/users',                
                headers=self.headers)
            #print('response is {}'.format(response))
            data = json.loads(response.data.decode())
            self.assertTrue(isinstance(data['status'], list))
    
    def test_list_users_byid_restapi(self):
        u1 = t.user_creation_for_test()
        with self.client:
            response = self.client.get('/list/user/u1')
            data = json.loads(response.data.decode())
            print(data)
            self.assertTrue(data['status'].get('username') == 'u1')
    
    
    def test_add_user_restapi(self):
        t.role_creation_for_test()
#         t.register_work_function_for_test()
        data = json.dumps(dict(
            name = 'u2',
            email = 'u2@abc.com',
            password = 'u2',
            wfc = 'wfc1',
            roles = ['role1']
            ))
        with self.client:
            response = self.client.post(
                '/add/user',
                data=data,
                content_type='application/json')
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'u2 has been registered.')     
            
    def test_add_dept_restapi(self):
        with self.client:
            response = self.client.post('/add/dept/dept1')
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'dept1 has been registered.')   
                  
 
    def test_add_orgunit_restapi(self):
        with self.client:
            response = self.client.post('/add/ou/ou1')
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'ou1 has been registered.')                  

    def test_add_org_restapi(self):
        with self.client:
            response = self.client.post('/add/org/org1')
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'org1 has been registered.')      

    def test_add_wfc_restapi(self):
        t.register_work_function_for_test
        with self.client:
            response = self.client.post('/add/wfc/wfc1')
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'wfc1 has been registered.')   
            
    def test_delete_user_restapi(self):
        u1 = t.user_creation_for_test()
        with self.client:
            response = self.client.delete('/delete/user/u1')
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'u1 has been  deleted successfully')
            
    def test_delete_org_restapi(self):
        u1 = t.create_org_for_test()
        with self.client:
            response = self.client.delete('/delete/org/org1')
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'org1 has been  deleted successfully')            
        
    def test_delete_ou_restapi(self):
        u1 = t.create_orgunit_for_test()
        with self.client:
            response = self.client.delete('/delete/ou/ou1')
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'ou1 has been  deleted successfully')     
 
    def test_delete_dept_restapi(self):
        u1 = t.create_dept_for_test()
        with self.client:
            response = self.client.delete('/delete/dept/dept1')
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'dept1 has been  deleted successfully')                
      
  
    def test_delete_wfc_restapi(self):
        u1 = t.register_work_function_for_test()
        with self.client:
            response = self.client.delete('/delete/wfc/wfc1')
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'wfc1 has been  deleted successfully')  
            
    def test_delete_role_restapi(self):
        u1 = t.role_creation_for_test()
        with self.client:
            response = self.client.delete('/delete/role/role1')
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'role1 has been  deleted successfully')   