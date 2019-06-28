from tokenleader.tests.base_test import BaseTestCase
from tokenleader.app1.catalog import catalog_functions as cf


service_name = 'testservice'
url_int = 'localhost/5005'
url_ext = 'localhost/5005'
url_admin = 'localhost/5005'


service_catalog = {'testservice': {'endpoint_url_internal': 'localhost/5005', 
                                     'name': 'testservice', 'endpoint_url_admin': 'localhost/5005',
                                     'endpoint_url_external': 'localhost/5005', 'id': 1}
                                     }

class TestCatalog(BaseTestCase):
    
    def add_service(self):
        r =cf.add_service( service_name, urlint=url_int, urlext=url_ext, urladmin=url_admin)
        return r
        
    def list_services(self):
        self.add_service()
        r = cf.list_services()
        return r
        
    def delete_service(self):
        self.add_service()
        r = cf.delete_service(service_name)
        return r