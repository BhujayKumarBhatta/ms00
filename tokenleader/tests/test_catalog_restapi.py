import json
from tokenleader.tests.base_test import  BaseTestCase
from tokenleader.tests.test_catalog_ops import TestCatalog
from tokenleader.tests.test_auth import TestToken
from tokenleader.app1.catalog import catalog_functions as cf
test_token_instance = TestToken()
t = TestCatalog()

class TestCatalogRestApi(BaseTestCase):
 
    def test_list_services_restapi(self):   
        u1 = t.list_services()   
#        r =cf.add_service( 'testservice', urlint='localhost:5005')
        with self.client:
            response = self.client.get('/list/services')
            data = json.loads(response.data.decode())
            print(data)
#            self.assertTrue(isinstance(data['status'], list))
#            self.assertTrue(data['status'].get('name') == 'testservice has been registered.')
            
    
    
    def test_add_service_restapi(self):
        u1 = t.test_add_service()
        with self.client:
            response = self.client.get('/add/service/tokenleader')
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'].get('name') == 'tokenleader')
                
 
    def test_add_service_restapix(self):
        u1 = t.add_service()
#         t.register_work_function_for_test()
        data = json.dumps(dict(
            name = 'testservice',
            pwd = 'password',
            urlint = 'localhost:5005',
            urlext= 'localhost:5005',
            urladmin = 'localhost:5005',
            ))
        print(data)
        with self.client:
            response = self.client.post(
                '/add/service',
                data=data,
                content_type='application/json')
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'testservice has been registered.')     
    
    def test_delete_service_restapi(self):
        u1 = t.delete_service()
        with self.client:
            response = self.client.delete('/delete/service/testservice')
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'testservice has been  deleted successfully')
    
 