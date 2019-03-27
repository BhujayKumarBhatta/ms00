from flask import request, Blueprint, jsonify, current_app,make_response
from tokenleader.app1.catalog import catalog_functions as cf
from tokenleaderclient.configs.config_handler import Configs    
from  tokenleaderclient.client.client import Client 
from tokenleaderclient.rbac.enforcer import Enforcer
from tokenleader.tests.test_catalog_ops import TestCatalog


catalog_bp = Blueprint('catalog_bp', __name__)
auth_config = Configs()
tlclient = Client(auth_config)
enforcer = Enforcer(tlclient)

   
@catalog_bp.route('/list/service/all', methods=['GET'])
@enforcer.enforce_access_rule_with_token('tokenleader.list_service')
def list_services(wfc):     
    record_list = cf.list_services()
    response_obj = {"status": record_list}
    return jsonify(response_obj)

@catalog_bp.route('/add/service', methods=['POST'])
@enforcer.enforce_access_rule_with_token('tokenleader.add_service')
def add_service(wfc):
    data_must_contain = ['service_name', 'urlint', 'urlext', 'urladmin']
    for k in data_must_contain:
        if k not in request.json:
            return {"status": " the request must have the following \
            information {}".data_must_contain}
    service_name = request.json['service_name']
    urlint = request.json['urlint']
    urlext = request.json['urlext']
    urladmin = request.json['urladmin']
    #print('i got the name from http argument {}'.format(username))
    record = cf.add_service(service_name, urlint, urlext, urladmin)
    response_obj = {"status": record}
    return jsonify(response_obj)
