from flask import request, Blueprint, jsonify, current_app,make_response
from tokenleader.app1.catalog import catalog_functions as cf
from tokenleaderclient.configs.config_handler import Configs    
from  tokenleaderclient.client.client import Client 
from tokenleaderclient.rbac.enforcer import Enforcer
from tokenleader.app1.adminops.adminops_restapi import adminops_bp

catalog_bp = Blueprint('catalog_bp', __name__)
auth_config = Configs()
tlclient = Client(auth_config)
enforcer = Enforcer(tlclient)

   
#@catalog_bp.route('/list/addservice/<servicename>/<pwd>/<urlint>/<urlext>/<urladmin>', methods=['GET'])
#@enforcer.enforce_access_rule_with_token('tokenleader.adminops.adminops_restapi.list_users')
#def add_service(wfc,servicename,pwd,urlint,urlext,urladmin):    
    
#    msg = cf.add_service(servicename, pwd, urlint, urlext, urladmin )     
#    return msg

@catalog_bp('/list/services', methods=['GET'])
def list_services(self):
#    services_dict = cf.list_service()
#    obj_json = {"name": services_dict.get('name')}
#    response_obj = {"status": obj_json}
#    return jsonify(response_obj)

    record_list = cf.list_services()
    response_obj = {"status": record_list}
    return jsonify(response_obj)
