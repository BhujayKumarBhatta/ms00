#from flask import Blueprint
#from tokenleader import app1   
#from app1.catalog import models_calalog 
#  # this import is required for flask db migrate to recognize the new model
# 
# 
#catalog_bp = Blueprint('catalog_bp', __name__)
#from tokenleader.app_run import app  
from sqlalchemy import exc
from tokenleader.app1 import db
from tokenleader.app1.catalog.models_catalog import  ServiceCatalog
#from app1.catalog import models_catalog as mc
#from app1.catalog.models_catalog import ServiceCatalog
from tokenleader.app1.authentication import models
from tokenleader.app1.authentication.models import User, Role, Workfunctioncontext, Organization, Orgunit, Department


def get_input(text):
    return input(text)


def add_service(name, pwd=None, urlint=None, urlext=None, urladmin=None ):
    record = ServiceCatalog(name=name, endpoint_url_internal=urlint, 
                       endpoint_url_external=urlext,
                       endpoint_url_admin=urladmin)
    if pwd:
        record.set_password(pwd)
    try:
        db.session.add(record)        
        db.session.commit()
        msg = "{} has been registered.".format(name)                
    except exc.IntegrityError:
        msg = ('databse integrity error, {} by the same name may be already present'.format(
            name))
        db.session.rollback()
        #raise
    except  Exception as e:
        msg =("{} could not be registered , the erro is: \n  {}".format(name, e))
        db.session.rollback()
    print(msg)    
    return msg


def list_services(cname=None):
    record = None
    record_list = []
    record_list_dic = []   
    if cname:
        record = ServiceCatalog.query.filter_by(name=cname).first()
        print(record.to_dict())
        return(record.to_dict())
    else:
        record_list = ServiceCatalog.query.all()
        for record in record_list:
            print(record.to_dict())
            record_list_dic.append(record)
        return record_list_dic
    
    
def delete_service(cname):
    record = ServiceCatalog.query.filter_by(name=cname).first()
    input_message = ('Are you sure to delete  :{},  with id {} \n'
                         'Type \'yes\' to confirm  deleting  or no to abort:  '.format(
                             record.name, record.id))    
                
    uinput = get_input(input_message)
    if uinput == 'yes':          
        try:
            db.session.delete(record)        
            db.session.commit()
            status = "{} has been  deleted successfully".format(cname) 
        except  Exception as e:
                    status = "{} could not be deleted , the erro is: \n  {}".format(cname, e)
                    print(status)
                    #return status
    else:
        status = 'Aborting deletion'
        print(status)    
    
    return status
    
#        
    