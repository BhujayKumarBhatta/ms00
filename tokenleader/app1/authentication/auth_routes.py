from flask import request, Blueprint, jsonify, current_app,make_response
from tokenleader.app1.authentication.authclass import TokenManager 

token_login_bp = Blueprint('token_login_bp', __name__)
objTokenMgr = TokenManager()
@token_login_bp.route('/token/gettoken', methods=['POST'])
def get_token():
    '''        
     curl -X POST -d '{"username": "test", "password": "test", "domain": "itc"}'  \
     -H "Content-Type: Application/json"  localhost:5001/token/gettoken

    curl -X POST -d '{"username": "test", "otp": "3376"}'  \
     -H "Content-Type: Application/json"  localhost:5001/token/gettoken
     
    curl -X POST -d '{"email": "test@xyz.com", "otp": "3376"}'  \
     -H "Content-Type: Application/json"  localhost:5001/token/gettoken
     
     1.  get the data from req , uname , pwd , org/domain
     2.  read and retrive  user info from  db :
        identify if the user is internal or extrenal 
        identify its auth source as db or ldap
        mail, sms. direct,  based on user database flag
        login by emailid , emailbased login allowed
     3.  authenticate password - ldap bind 
     4. otp generation
     5. otp_deliery -  
     4. token_generation ( based on internal     
     4. token_generation (userifo, otp,)
        based on  internal or external 
          
    '''
     
    #gettoken_by_usr_pwd(request)
    #gettoken_by_usr_otp(request)gettoken_by_usr_pwd
    #gettoken_by_email_otp(request)
    
    # CASE 1: Username & Otp      
    if 'username' in request.json and 'otp' in request.json:  
        return objTokenMgr.get_token_by_otp(request)
    # Case 2: Username & Passwordgettoken_by_usr_pwd
    elif 'username' in request.json and 'password' in request.json and 'domain' in request.json:
        return objTokenMgr.get_token_or_otp(request)
    # Case 3: Email & Otp
    elif 'email' in request.json and 'otp' in request.json:
        return objTokenMgr.gettoken_by_email_otp(request)
    else:
        responseObject = {
            'status': 'restricted',
            'message': 'invalid request',}
        return jsonify(responseObject)
          
        
@token_login_bp.route('/token/verify_token', methods=['GET'])
def verify_token():
    '''
    curl -H  "X-Auth-Token:<paste toekn here>"  localhost:5001/token/verify_token
    '''
    publickey = current_app.config.get('public_key')
    if 'X-Auth-Token' in request.headers:
        auth_token = request.headers.get('X-Auth-Token')
        payload = objTokenMgr.decrypt_n_verify_token(auth_token, publickey)
        if payload == "Signature expired. Please log in again." :
            status = "Signature expired"
            message = "Signature expired. Please log in and get a fresh token and send it for reverify."
        elif payload == "Invalid token. Please log in again.":
            status = "Invalid token"
            message = "Invalid token. obtain a valid token and send it for verifiaction"
        else:
            status = "Verification Successful"
            message = "Token has been successfully decrypted"
    else:
        status = "request header  missing 'X-Auth-Token' key or token value"
        message = "The request header must carry a 'X-Auth-Token' key whose value should be a valid JWT token  "
        payload = {}
    responseObject = {
                        'status': status,
                        'message': message,
                        'payload': payload
                     }
#                     return auth_token
    return make_response(jsonify(responseObject)), 201
#