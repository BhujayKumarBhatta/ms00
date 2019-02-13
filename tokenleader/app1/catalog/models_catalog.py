from tokenleader.app1 import db
from flask import  current_app
from werkzeug.security import generate_password_hash, check_password_hash
'''
ServiceCatalogue
-------------------------
name
service_account_name
servie_account_password
service_endpoints --- one to many relationship to  service_endpoints
or :
internal_endpoint_url
external_enpoint_url
admin_endpoint_url

from app1 import db
from app1.catalogue.models import ServiceCatalogue
s1 = ServiceCatalogue(name='s1', endpoint_url_internal='localhost:5002', endpoint_url_external='10.0.0.1:5002')
db.session.add(s1)
db.session.commit()

'''

class ServiceCatalog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)      
    password_hash = db.Column(db.String(128))
    endpoint_url_internal = db.Column(db.String(256), index=True, unique=True)
    endpoint_url_external = db.Column(db.String(256), index=True, unique=True)
    endpoint_url_admin = db.Column(db.String(256), index=True, unique=True) 
    
    def __repr__(self):
        return '<Service {}>'.format(self.name)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
     
    def check_password(self, password):
        return  check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        data = {
            'id': self.id,
            'name': self.name,
            'endpoint_url_internal': self.endpoint_url_internal,
            'endpoint_url_external': self.endpoint_url_external,
            'endpoint_url_admin': self.endpoint_url_admin
            }
        return data  
    

