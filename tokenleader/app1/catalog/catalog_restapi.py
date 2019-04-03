from flask import request, Blueprint, jsonify, current_app, make_response
from tokenleader.app1.catalog import catalog_functions as cf
from tokenleaderclient.configs.config_handler import Configs    
from  tokenleaderclient.client.client import Client 
from tokenleaderclient.rbac.enforcer import Enforcer
#from tokenleader.tests.test_catalog_ops import TestCatalog


catalog_bp = Blueprint('catalog_bp', __name__)
auth_config = Configs()
tlclient = Client(auth_config)
enforcer = Enforcer(tlclient)

@catalog_bp.route('/list/services', methods=['GET'])
# @enforcer.enforce_access_rule_with_token('tokenleader.list_services')
def list_services():  
    '''
    the function must have a mandatory wfc paramater for applying enforcer decorator
    '''    
    record = cf.list_services()
    print(record)
    response_obj = {"status": record}
    return jsonify(response_obj)

      
@catalog_bp.route('/list/service/<srvname>', methods=['GET'])
# @enforcer.enforce_access_rule_with_token('tokenleader.list_services')
def list_services_byname(srvname):  
    record = cf.list_services(srvname)
    response_obj = {"status": record}
    return jsonify(response_obj)
 
