import json
from tokenleader.tests.base_test import  BaseTestCase
from tokenleader.tests.test_catalog_ops import TestCatalog
from tokenleader.tests.test_auth import TestToken
test_token_instance = TestToken()
t = TestCatalog()

class TestCatalogRestApi(BaseTestCase):
 
    def test_list_services_restapi(self):      
        u1 = t.list_services()
        with self.client:
            response = self.client.get('/list/service/tokenleader')
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'].get('name') == 'tokenleader')
            
            
    def test_add_service_restapi(self):      
        u1 = t.add_service()
        with self.client:
            response = self.client.post('/add/service')
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'].get('name') == 'tokenleader has been registered.')           