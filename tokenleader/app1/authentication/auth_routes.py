from flask import request, Blueprint, jsonify, current_app,make_response
from tokenleader.app1.authentication.authenticator import Authenticator

token_login_bp = Blueprint('token_login_bp', __name__)

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
        responseObject = objTokenMgr.decrypt_n_verify_token(auth_token, publickey)
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
