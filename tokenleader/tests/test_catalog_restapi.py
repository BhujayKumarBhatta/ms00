from flask import request, Blueprint, jsonify, current_app,make_response
from tokenleader.app1.catalog import catalog_functions as cf , catalog_bp
from tokenleaderclient.configs.config_handler import Configs    
from tokenleaderclient.client.client import Client 
from tokenleaderclient.rbac.enforcer import Enforcer
from tokenleader.app1.adminops.adminops_restapi import adminops_bp

adminops_bp = Blueprint('adminops_bp' , __name__)
auth_config = Configs()
tlclient = Client(auth_config)
enforcer = Enforcer(tlclient)
 
   
#@catalog_bp.route('/list/addservice/<servicename>/<pwd>/<urlint>/<urlext>/<urladmin>', methods=['GET'])
#@enforcer.enforce_access_rule_with_token('tokenleader.adminops.adminops_restapi.list_users')
#def add_service(wfc,servicename,pwd,urlint,urlext,urladmin):    
    
#    msg = cf.add_service(servicename, pwd, urlint, urlext, urladmin )     
#    return msg

@adminops_bp.route('/list/services', methods=['GET'])
def list_services():    
     
    record_list = cf.list_services()
    response_obj = {"status": record_list}
    return jsonify(response_obj)