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

@catalog_bp.route('/add/service/<name>', methods=['POST'])
@enforcer.enforce_access_rule_with_token('tokenleader.add_service')
def add_service(wfc):   
    status = cf.add_service
    response_obj = {"status": status}
    return jsonify(response_obj)
