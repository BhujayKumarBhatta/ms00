import json
from tokenleader.tests.base_test import  BaseTestCase
from tokenleader.tests.test_catalog_ops import TestCatalog
from tokenleader.tests.test_auth import TestToken
test_token_instance = TestToken()
tc = TestCatalog()

class TestCatalogRestApi(BaseTestCase):
 
    def test_list_services_restapi(self):      
        u1 = tc.list_services()
#        print(u1)
        with self.client:
            response = self.client.get('/list/service/all')
            print(response)
            data = json.loads(response.data.decode())
#           self.assertTrue(isinstance(data['status'], list))
            print(data)
            self.assertTrue(data['status'].get('name') == 'microservice1')
            
            
           