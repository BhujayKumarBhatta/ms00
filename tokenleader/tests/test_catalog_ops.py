from tokenleader.app1 import db
from tokenleader.app1.catalog.models_catalog import ServiceCatalog
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
    
    def  add_service(self):
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
    
    def test_add_service(self):
        msg = self.add_service()        
        self.assertTrue(msg == "testservice has been registered.")
        
    def test_service_catalog_format(self):        
        svcs = self.list_services()
#         svcs = ServiceCatalog.query.all()
        service_catalog_created= {}
        for s in svcs:
            service_catalog_created[s.name]=s.to_dict()
#         print(service_catalog)
#         print(service_catalog_created)  
        self.assertTrue(service_catalog_created == service_catalog)
        
        
        