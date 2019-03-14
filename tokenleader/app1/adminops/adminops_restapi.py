from flask import request, Blueprint, jsonify, current_app,make_response
from tokenleader.app1.adminops import admin_functions as af
from tokenleaderclient.configs.config_handler import Configs    
from  tokenleaderclient.client.client import Client 
from tokenleaderclient.rbac.enforcer import Enforcer

adminops_bp = Blueprint('adminops_bp', __name__)
auth_config = Configs()
tlclient = Client(auth_config)
enforcer = Enforcer(tlclient)
 
@adminops_bp.route('/list/users', methods=['GET'])
@enforcer.enforce_access_rule_with_token('tokenleader.adminops.adminops_restapi.list_users')
def list_users(wfc):
    '''
    the function must have a mandatory wfc paramater for applying enforcer decorator
    '''
    record_list = af.list_users()
    response_obj = {"status": record_list}
    return jsonify(response_obj)

@adminops_bp.route('/list/user/<username>', methods=['GET'])
def list_user_byname(username):
    #print('i got the name from http argument {}'.format(username))
    record = af.list_users(username)
    response_obj = {"status": record}
    return jsonify(response_obj)


@adminops_bp.route('/add/user', methods=['POST'])
def add_user():
    data_must_contain = ['name', 'email', 'password', 'wfc', 'roles']
    for k in data_must_contain:
        if k not in request.json:
            return {"status": " the request must have the following \
            information {}".data_must_contain}
    uname = request.json['name']
    email = request.json['email']
    pwd = request.json['password']
    wfc_name  = request.json['wfc']
    roles = request.json['roles']
    #print('i got the name from http argument {}'.format(username))
    record = af.register_user(uname, email, pwd, wfc_name, roles=roles)
    response_obj = {"status": record}
    return jsonify(response_obj)

@adminops_bp.route('/add/dept/<deptname>', methods=['POST'])
def add_dept_restapi(deptname):   
    status = af.register_dept(deptname)
    response_obj = {"status": status}
    return jsonify(response_obj)

@adminops_bp.route('/add/ou/<ouname>', methods=['POST'])
def add_orgunit_restapi(ouname):   
    status = af.register_ou(ouname)
    response_obj = {"status": status}
    return jsonify(response_obj)

@adminops_bp.route('/add/org/<orgname>', methods=['POST'])
def add_org_restapi(orgname):   
    status = af.register_org(orgname)
    response_obj = {"status": status}
    return jsonify(response_obj)

@adminops_bp.route('/add/wfc/<wfcname>', methods=['POST'])
def add_wfc_restapi(wfcname):   
    status = af.register_work_func_context(options.name, options.wfcorg, options.wfcou, options.wfcdept)
    response_obj = {"status": status}
    return jsonify(response_obj)

@adminops_bp.route('/delete/user/<username>', methods=['DELETE'])
def delete_user_restapi(username):   
    status = af.delete_user(username)
    response_obj = {"status": status}
    return jsonify(response_obj)

@adminops_bp.route('/delete/ou/<ouname>', methods=['DELETE'])
def delete_ou_restapi(ouname):
    status = af.delete_ou(ouname)
    response_obj = {"status": status}
    return jsonify(response_obj)

@adminops_bp.route('/delete/org/<orgname>', methods=['DELETE'])
def delete_org_restapi(orgname):
    status = af.delete_org(orgname)
    response_obj = {"status": status}
    return jsonify(response_obj)

@adminops_bp.route('/delete/dept/<deptname>', methods=['DELETE'])
def delete_dept_restapi(deptname):
    status = af.delete_dept(deptname)
    response_obj = {"status": status}
    return jsonify(response_obj)

@adminops_bp.route('/delete/role/<rolename>', methods=['DELETE'])
def delete_role_restapi(rolename):
    status = af.delete_role(rolename)
    response_obj = {"status": status}
    return jsonify(response_obj)

@adminops_bp.route('/delete/wfc/<wfcname>', methods=['DELETE'])
def delete_wfc_restapi(wfcname):
    status = af.delete_wfc(wfcname)
    response_obj = {"status": status}
    return jsonify(response_obj)

@adminops_bp.route('/list/org', methods=['GET'])
@enforcer.enforce_access_rule_with_token('tokenleader.adminops.adminops_restapi.list_org')
def list_org(wfc):
    org_dict = af.list_org()
    obj_json = {"name": org_dict.get('name')}
    response_obj = {"status": obj_json}
    return jsonify(response_obj)

@adminops_bp.route('/list/dept', methods=['GET'])
@enforcer.enforce_access_rule_with_token('tokenleader.adminops.adminops_restapi.list_dept')
def list_dept(wfc):
    dept_dict = af.list_dept()
    obj_json = {"name": dept_dict.get('name')}
    response_obj = {"status": obj_json}
    return jsonify(response_obj)

@adminops_bp.route('/list/role', methods=['GET'])
@enforcer.enforce_access_rule_with_token('tokenleader.adminops.adminops_restapi.list_role')
def list_role(wfc):
    role_dict = af.list_role()
    obj_json = {"name": role_dict.get('name')}
    response_obj = {"status": obj_json}
    return jsonify(response_obj)

@adminops_bp.route('/list/ou', methods=['GET'])
@enforcer.enforce_access_rule_with_token('tokenleader.adminops.adminops_restapi.list_ou')
def list_ou(wfc):
    ou_dict = af.list_ou()
    obj_json = {"name": ou_dict.get('name')}
    response_obj = {"status": obj_json}
    return jsonify(response_obj)


