from flask import request, Blueprint, jsonify, current_app,make_response
import jwt
import datetime
from app1.authentication.models import User 
# from flask.globals import session


token_login_bp = Blueprint('token_login_bp', __name__)

# don't try to access it here to avoid RuntimeError: Working outside of application context
#publickey = current_app.config.get('public_key') 


def generate_encrypted_auth_token(payload, priv_key):
    try: 
        #print("inside the func start")       
        auth_token = jwt.encode(
             payload,
             priv_key,
             algorithm='RS512'
        )  
        #print("type of auth_token within the func is {}".format(type(auth_token)))
        return auth_token  
        #print("inside the func last line")                                
    except Exception as e:
                    return e
                
def decrypt_n_verify_token(auth_token, pub_key):
    try:
        payload = jwt.decode(
            auth_token,
            pub_key,
            algorithm=['RS512']
        )
        
        return payload
#         
    except jwt.ExpiredSignatureError:
            return 'Signature expired. Please log in again.'
    except jwt.InvalidTokenError:
            return 'Invalid token. Please log in again.'

@token_login_bp.route('/token/gettoken', methods=['POST'])
def get_token():
    '''        
     curl -X POST -d '{"username": "admin", "password": "admin"}'  \
     -H "Content-Type: Application/json"  localhost:5001/token/gettoken
     '''
    if request.method == 'POST':
        if 'username' in request.json and 'password' in request.json:
            username = request.json['username']
            password = request.json['password'] 
            
            if username is None or password is None:
                responseObject = {
                        'status': 'missing authentication info ',
                        'message': 'no authentication information provided',}
                return jsonify(responseObject) 
                      
            user = User.query.filter_by(username=username).first()
            if user is None:
                responseObject = {
                        'status': 'User not registered',
                        'message': 'user not found, not registered yet',}
                return jsonify(responseObject )
               
            if user.check_password(password):
                user_from_db = user.to_dict()
    
                privkey = current_app.config.get('private_key')     
                
                payload = {
                    'exp': datetime.datetime.utcnow() + datetime.timedelta(days=0, seconds=3600),
                    'iat': datetime.datetime.utcnow(),
                    'sub': user_from_db
                     }
#                 print(payload)
                
                try:
                    auth_token = jwt.encode(
                        payload,
                        privkey,
                        algorithm = 'RS512')
                
                except Exception as e:
                    return e
                #auth_token = generate_encrypted_auth_token(payload, priv_key)
                #print(auth_token)
                responseObject = {
                        'status': 'success',
                        'message': '',
                        'auth_token': auth_token.decode()}
            #         return auth_token
                return make_response(jsonify(responseObject)), 201
            else:
                responseObject = {
                        'status': 'Wrong Password',
                        'message': 'Password did not match',}
                return jsonify(responseObject)
                
            
                
    
@token_login_bp.route('/token/verify_token', methods=['GET'])
def verify_token():    
    '''
    curl -H  "X-Auth-Token:<paste toekn here>"  localhost:5001/token/verify_token    
    
    '''
    publickey = current_app.config.get('public_key')
    
    if 'X-Auth-Token' in request.headers:
        auth_token = request.headers.get('X-Auth-Token')
        payload = decrypt_n_verify_token(auth_token, publickey) 
        
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
                        'payload': payload}
            #         return auth_token
    return make_response(jsonify(responseObject)), 201       
#    


# '''
# Following are the claim attributes :
# iss: The issuer of the token
# sub: The subject of the token
# aud: The audience of the token
# qsh: query string hash
# exp: Token expiration time defined in Unix time
# nbf: “Not before” time that identifies the time before which the JWT must not be accepted for processing
# iat: “Issued at” time, in Unix time, at which the token was issued
# jti: JWT ID claim provides a unique identifier for the JWT
# 
# '''
