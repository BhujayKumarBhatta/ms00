import json
from tokenleader.tests.base_test import  BaseTestCase
from tokenleader.tests.catalog_ops import TestCatalog
# from tokenleader.app1.catalog import catalog_functions as cf
# from tokenleader.tests.test_auth import TestToken
# test_token_instance = TestToken()


t = TestCatalog()

class TestCatalogRestApi(BaseTestCase):
 
    def test_list_services_restapi(self):
        #token_in_byte = self.get_auth_token_with_actual_rsa_keys_fake_user()
        token_in_byte = self.get_auth_token_with_actual_rsa_keys_fake_user()
        t.add_service()
        print(self.client)
        with self.client:
            self.headers = {'X-Auth-Token': token_in_byte}
            response = self.client.get(
                '/list/services',                
                headers=self.headers)
#             print(response)
            # content_type='application/json'
            data = json.loads(response.data.decode())
#             print(data)
            self.assertTrue(isinstance(data['status'], list)) 
              
  
    def test_add_service_restapi(self):
        token_in_byte = self.get_auth_token_with_actual_rsa_keys_fake_user()
        data = json.dumps(dict(
            name = 'testservice',
            urlint = 'localhost:5005',
            urlext= 'localhost:5005',
            urladmin = 'localhost:5005',
            ))
        with self.client:
            self.headers = {'X-Auth-Token': token_in_byte}
            response = self.client.post(
                '/add/service',
                data=data,
                headers=self.headers,
                content_type='application/json')
#             print(response)
            data = json.loads(response.data.decode())
#             print(data)
            self.assertTrue(data['status'] == 'testservice has been registered.')     
     
    def test_delete_service_restapi(self):
        token_in_byte = self.get_auth_token_with_actual_rsa_keys_fake_user()
        data = json.dumps(dict(
            name = 'testservice',
            ))
        t.add_service()
        with self.client:
            self.headers = {'X-Auth-Token': token_in_byte}
            response = self.client.delete(
                '/delete/service',
                data=data,
                headers=self.headers,
                content_type='application/json')
#             print(response)
            data = json.loads(response.data.decode())
#             print(data)
            self.assertTrue(data['status'] == 'testservice has been  deleted successfully')
     
  