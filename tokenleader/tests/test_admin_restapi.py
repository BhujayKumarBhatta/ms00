import json
from tokenleader.tests.base_test import  BaseTestCase
from tokenleader.tests.admin_ops import TestUserModel
# from tokenleader.tests.test_auth import TestToken
# test_token_instance = TestToken()
# t = TestUserModel()

class TestAdminRestApi(TestUserModel):
    '''REMEMBER CLIENT_CONFIG FILE TL_PUBLIC_KEY WILL BE  
    THE ID_RSA_PUB FROM THE TEST DATA FOLDER  FOR THIS TEST.
    THIS IS REQUIRED IF THE KEY FILE SETTINGS IN THE TOKENLEADERC-CONG(TEST)
    IS SET TO TESTLOCATION'''
    def test_list_users_without_token(self):
        u1 = self.user_creation_for_test()        
        with self.client:
            response = self.client.get('/list/users')
#             print('response is {}'.format(response))
            data = json.loads(response.data.decode())
            #print(data)
            txt = 'this endpoint is restricted , authenticaton or authorization failed'
            self.assertTrue(txt in  data['message'] )
             
    def test_list_users_with_token(self):
        u1 = self.user_creation_for_test()
        token_in_byte = self.get_auth_token_with_actual_rsa_keys_fake_user()
        #print(token_in_byte)
        # print(self.client)
        with self.client:
            self.headers = {'X-Auth-Token': token_in_byte}
            response = self.client.get(
                '/list/users',                
                headers=self.headers)
            #print('response is {}'.format(response))
            data = json.loads(response.data.decode())
            self.assertTrue(isinstance(data['status'], list))
     
#     def test_list_users_with_token_of_external_user(self):
#         u1 = self.external_user_creation_for_test()
#         token_in_byte = self.get_auth_token_with_actual_rsa_keys_fake_user()
#         #print(token_in_byte)
#         with self.client:
#             self.headers = {'X-Auth-Token': token_in_byte}
#             response = self.client.get(
#                  '/list/users',                
#                  headers=self.headers)
#             #print('response is {}'.format(response))
#             data = json.loads(response.data.decode())
#             self.assertTrue(isinstance(data['status'], list))
  
    def test_list_users_byid_restapi(self):
        u1 = self.user_creation_for_test()
        token_in_byte = self.get_auth_token_with_actual_rsa_keys_fake_user()
        with self.client:
            self.headers = {'X-Auth-Token': token_in_byte}
            response = self.client.get(
                '/list/user/u1',                
                headers=self.headers)
            # response = self.client.get('/list/user/u1')
            data = json.loads(response.data.decode())
#            print(data)
            self.assertTrue(data['status'].get('username') == 'u1')
  
    def test_list_dept_restapi(self):
#         u1 = t.test_register_dept()
        u1 = self.user_creation_for_test()
        token_in_byte = self.get_auth_token_with_actual_rsa_keys_fake_user()
        with self.client:
            self.headers = {'X-Auth-Token': token_in_byte}
            response = self.client.get(
                '/list/dept',                
                headers=self.headers)
            data = json.loads(response.data.decode())
            self.assertTrue(isinstance(data['status'], list))
            print(data)
 #           self.assertTrue(data['status'].get('deptname') == 'dept1')                     
   
         
    def test_add_user_restapi_fails_for_password_complaince(self):
#         t.role_creation_for_test()
        u1 = self.user_creation_for_test()
        token_in_byte = self.get_auth_token_with_actual_rsa_keys_fake_user()
#         t.register_work_function_for_test()
        data = json.dumps(dict(
            username = 'u2',
            email = 'u2@abc.com',
            password = 'u2',
            wfc = 'wfc1',
            roles = ['role1'],
            created_by = 'u1'
            ))
        print(data)
        with self.client:
            self.headers = {'X-Auth-Token': token_in_byte}
            response = self.client.post(
                '/add/user',
                data=data,
                headers=self.headers,
                content_type='application/json')
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'PasswordLengthError')
            
    
    def test_add_user_restapi_sucess(self):
#         t.role_creation_for_test()
        u1 = self.user_creation_for_test()
        token_in_byte = self.get_auth_token_with_actual_rsa_keys_fake_user()
#         t.register_work_function_for_test()
        data = json.dumps(dict(
            username = 'u2',
            email = 'u2@abc.com',
            password = 'Secret@12',
            wfc = 'wfc1',
            roles = ['role1'],
            created_by = 'u1'
            ))
        print(data)
        with self.client:
            self.headers = {'X-Auth-Token': token_in_byte}
            response = self.client.post(
                '/add/user',
                data=data,
                headers=self.headers,
                content_type='application/json')
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'u2 has been registered.')

    def test_add_wfc_restapi(self):
        u1 = self.user_creation_for_test()
        token_in_byte = self.get_auth_token_with_actual_rsa_keys_fake_user()
        data = json.dumps(dict(
            fname = 'wfc3',
            orgname = 'org1',
            ou_name = 'ou1',
            dept_name = 'dept1',
            created_by = 'u1',   
            ))
        with self.client:
            self.headers = {'X-Auth-Token': token_in_byte}
            response = self.client.post(
                '/add/wfc',
                data=data,
                headers=self.headers,
                content_type='application/json')
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'wfc3 has been registered.')              
     
              
    def test_add_dept_restapi(self):
        u1 = self.user_creation_for_test()
        token_in_byte = self.get_auth_token_with_actual_rsa_keys_fake_user()
        data = json.dumps(dict(
            created_by = 'u1',            
            deptname = 'dept3',
            ))
        with self.client:
            self.headers = {'X-Auth-Token': token_in_byte}
            response = self.client.post('/add/dept',
                        data=data,
                        headers=self.headers,
                        content_type='application/json')
                          
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'dept3 has been registered.')   
                    
   
    def test_add_orgunit_restapi(self):
        u1 = self.user_creation_for_test()
        token_in_byte = self.get_auth_token_with_actual_rsa_keys_fake_user()
        data = json.dumps(dict(
            created_by = 'u1',            
            ouname = 'ou3',
            ))
        with self.client:
            self.headers = {'X-Auth-Token': token_in_byte}
            response = self.client.post('/add/ou',
                        data=data,
                        headers=self.headers,
                        content_type='application/json')
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'ou3 has been registered.')                  
  
    def test_add_org_restapi(self):
        u1 = self.user_creation_for_test()
        token_in_byte = self.get_auth_token_with_actual_rsa_keys_fake_user()
        data = json.dumps(dict(
            created_by = 'u1',            
            oname = 'org3',
            ))
        with self.client:
            self.headers = {'X-Auth-Token': token_in_byte}
            response = self.client.post('/add/org',
                        data=data,
                        headers=self.headers,
                        content_type='application/json')
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'org3 has been registered.')   
                 
    def test_add_role_restapi(self):
        u1 = self.user_creation_for_test()
        token_in_byte = self.get_auth_token_with_actual_rsa_keys_fake_user()
        data = json.dumps(dict(
            created_by = 'u1',            
            rolename = 'role3',
            ))
        with self.client:
            self.headers = {'X-Auth-Token': token_in_byte}
            response = self.client.post('/add/role',
                        data=data,
                        headers=self.headers,
                        content_type='application/json')
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'role3 has been registered.')      
   
    def test_delete_user_restapi(self):
        u1 = self.user_creation_for_test()
        token_in_byte = self.get_auth_token_with_actual_rsa_keys_fake_user()
        data = json.dumps(dict(          
            username = 'u1',
            ))
        with self.client:
            self.headers = {'X-Auth-Token': token_in_byte}
            response = self.client.delete('/delete/user',
                        data=data,
                        headers=self.headers,
                        content_type='application/json')
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'u1 has been  deleted successfully')
              
    def test_delete_org_restapi(self):
#         u1 = t.user_creation_for_test()
        u2 = self.create_org_for_test()
        token_in_byte = self.get_auth_token_with_actual_rsa_keys_fake_user()
        data = json.dumps(dict(          
            oname = 'org1',
            ))
        with self.client:
            self.headers = {'X-Auth-Token': token_in_byte}
            response = self.client.delete('/delete/org',
                        data=data,
                        headers=self.headers,
                        content_type='application/json')
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'org1 has been  deleted successfully')            
          
    def test_delete_ou_restapi(self):
#         u1 = t.user_creation_for_test()
        u2 = self.create_orgunit_for_test()
        token_in_byte = self.get_auth_token_with_actual_rsa_keys_fake_user()
        data = json.dumps(dict(          
            ouname = 'ou1',
            ))
        with self.client:
            self.headers = {'X-Auth-Token': token_in_byte}
            response = self.client.delete('/delete/ou',
                        data=data,
                        headers=self.headers,
                        content_type='application/json')
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'ou1 has been  deleted successfully')     
   
    def test_delete_dept_restapi(self):
#         u1 = t.user_creation_for_test()
        u2 = self.create_dept_for_test()
        token_in_byte = self.get_auth_token_with_actual_rsa_keys_fake_user()
        data = json.dumps(dict(          
            deptname = 'dept1',
            ))
        with self.client:
            self.headers = {'X-Auth-Token': token_in_byte}
            response = self.client.delete('/delete/dept',
                        data=data,
                        headers=self.headers,
                        content_type='application/json')
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'dept1 has been  deleted successfully')                
        
    
    def test_delete_wfc_restapi(self):
#         u1 = t.user_creation_for_test()
        u2 = self.register_work_function_for_test()
        token_in_byte = self.get_auth_token_with_actual_rsa_keys_fake_user()
        data = json.dumps(dict(          
            wfcname = 'wfc1',
            ))
        with self.client:
            self.headers = {'X-Auth-Token': token_in_byte}
            response = self.client.delete('/delete/wfc',
                        data=data,
                        headers=self.headers,
                        content_type='application/json')
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'wfc1 has been  deleted successfully')  
              
    def test_delete_role_restapi(self):
#         u1 = t.user_creation_for_test()
        u2 = self.role_creation_for_test()
        token_in_byte = self.get_auth_token_with_actual_rsa_keys_fake_user()
        data = json.dumps(dict(          
            rolename = 'role1',
            ))
        with self.client:
            self.headers = {'X-Auth-Token': token_in_byte}
            response = self.client.delete('/delete/role',
                        data=data,
                        headers=self.headers,
                        content_type='application/json')
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'role1 has been  deleted successfully')         
     