import json
from flask import request, Blueprint, jsonify, current_app,make_response
from tokenleader.app1.authentication.authenticator import Authenticator
from tokenleader.app1.authentication.tokenmanager import TokenManager
from tokenleader.app1.authentication.password_policy import Pwdpolicy
from tokenleader.app1.utils import common_utils

from tokenleaderclient.configs.config_handler import Configs
from  tokenleaderclient.client.client import Client
from tokenleaderclient.rbac.enforcer import Enforcer
from alembic.util.messaging import err




token_login_bp = Blueprint('token_login_bp', __name__)
auth_config = Configs()
tlclient = Client(auth_config)
enforcer = Enforcer(tlclient)

@token_login_bp.route('/token/gettoken', methods=['POST'])
def get_token():
    '''        
     curl -X POST -d '{"username": "test", "password": "test", "domain": "itc"}'  \
     -H "Content-Type: Application/json"  localhost:5001/token/gettoken

    curl -X POST -d '{"username": "test", "otp": "3376"}'  \
     -H "Content-Type: Application/json"  localhost:5001/token/gettoken
     
    curl -X POST -d '{"email": "test@xyz.com", "otp": "3376"}'  \
     -H "Content-Type: Application/json"  localhost:5001/token/gettoken
 
    '''    
    authobj = Authenticator(request)
    responseObject = authobj.authenticate()
    return make_response(jsonify(responseObject)), 201


@token_login_bp.route('/token/verify_token', methods=['GET'])
def verify_token():
    '''
    curl -H  "X-Auth-Token:<paste toekn here>"  localhost:5001/token/verify_token
    '''
    publickey = current_app.config.get('public_key')
    if 'X-Auth-Token' in request.headers:        
        auth_token = request.headers.get('X-Auth-Token')
        tmObj = TokenManager()
        responseObject = tmObj.decrypt_n_verify_token(auth_token, publickey)
    else:
        status = "request header  missing 'X-Auth-Token' key or token value"
        message = ("The request header must carry a 'X-Auth-Token'"
                   " key whose value should be a valid JWT token  ")
        payload = {}
        responseObject = {'status': status, 'message': message, 'payload': payload
                     }
#                     return auth_token
    return make_response(jsonify(responseObject)), 201
#

@token_login_bp.route('/change_pwd', methods=['POST'])
@enforcer.enforce_access_rule_with_token('tokenleader.change_password')
def  change_password(wfc):
    cfg = common_utils.reload_configs()
    policy_config = cfg.get('pwdpolicy')
    pwdpolicyObj = Pwdpolicy(policy_config)
    data_must_contain = ['username', 'new_password', 'old_password']
    for k in data_must_contain:
        if k not in request.json:
            return jsonify({"status": " the request must have the following \
            information {}".format(json.dumps(data_must_contain))})
    username = request.json['username']
    new_password = request.json['new_password']
    old_password = request.json['old_password']
    try:
        result = pwdpolicyObj.set_password(username, new_password, old_password)
        if result: result = "Password has been changed successfully"
    except Exception as err:
        if isinstance(err, dict) and 'status' in err.keys():
            result = err
        else:
            result = {'status': err}
    return jsonify(result)
    