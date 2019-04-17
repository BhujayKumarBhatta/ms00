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
@enforcer.enforce_access_rule_with_token('tokenleader.list_services')
def list_services():  
    '''
    the function must have a mandatory wfc paramater for applying enforcer decorator
    '''    
    record = cf.list_services()
    print(record)
    response_obj = {"status": record}
    return jsonify(response_obj)

      
@catalog_bp.route('/list/service/<srvname>', methods=['GET'])
@enforcer.enforce_access_rule_with_token('tokenleader.list_services_byname')
def list_services_byname(srvname):  
    record = cf.list_services(srvname)
    response_obj = {"status": record}
    return jsonify(response_obj)
 
@catalog_bp.route('/add/service', methods=['POST'])
@enforcer.enforce_access_rule_with_token('tokenleader.add_service')
def add_service():
    data_must_contain = ['name', 'urlint', 'urlext','urladmin']
    for k in data_must_contain:
        if k not in request.json:
            return {"status": " the request must have the following \
            information {}".data_must_contain}
    name = request.json['name']
#    pwd = request.json['pwd']
    urlint  = request.json['urlint']
    urlext = request.json['urlext']
    urladmin = request.json['urladmin']
    #print('i got the name from http argument {}'.format(username))
    record = cf.add_service(name, urlint, urlext, urladmin)
    response_obj = {"status": record}
    return jsonify(response_obj)

@catalog_bp.route('/delete/service/<srvname>', methods=['DELETE'])
@enforcer.enforce_access_rule_with_token('tokenleader.delete_service_byname')
def delete_service_byname(srvname):   
    status = cf.delete_service(srvname)
    response_obj = {"status": status}
    return jsonify(response_obj)

@catalog_bp.route('/delete/service', methods=['DELETE'])
@enforcer.enforce_access_rule_with_token('tokenleader.delete_service')
def delete_service():
    data_must_contain = ['name']
    for k in data_must_contain:
        if k not in request.json:
            return jsonify({"status": " the request must have the following \
            information {}".format(json.dumps(data_must_contain))})
    name = request.json['name']
    print('i got the name from http argument {}'.format(name))
    record = cf.delete_service(name)
    response_obj = {"status": record}
    return jsonify(response_obj)

