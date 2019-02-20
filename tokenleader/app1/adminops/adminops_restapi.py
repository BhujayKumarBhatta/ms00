from flask import request, Blueprint, jsonify, current_app,make_response
from tokenleader.app1.adminops import admin_functions as af
from tokenleaderclient.rbac import enforcer

adminops_bp = Blueprint('adminops_bp', __name__)
 
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


@adminops_bp.route('/delete/user/<username>', methods=['DELETE'])
def delete_user_restapi(username):   
    status = af.delete_user(username)
    response_obj = {"status": status}
    return jsonify(response_obj)

