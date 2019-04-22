from flask import request, Blueprint, jsonify, current_app,make_response
import jwt
import datetime
import requests
import json
import random
import ldap
from tokenleader.app1 import db, app
from tokenleader.app1.authentication.models import User, Organization, Otp 
from tokenleader.app1.catalog.models_catalog import ServiceCatalog
# from flask.globals import session


token_login_bp = Blueprint('token_login_bp', __name__)

# don't try to access it here to avoid RuntimeError: Working outside of application context
#publickey = current_app.config.get('public_key') 

def generate_one_time_password(userid):
    rand = str(random.random())
    otp = rand[-4:]
    record = Otp(otp=otp,userid=userid,creation_date=datetime.datetime.utcnow)
    db.session.add(record)
    db.session.commit()
    mail_to = user_from_db['email']
    r = requests.post(url='http://10.174.112.79:5000/mail', data=json.dumps({'mail_to':mail_to, 'otp':otp}))
    if r.status_code == 200:
        responseObject = {
            'status': 'success',
            'message': r.text,}
        return jsonify(responseObject )
    else:
        responseObject = {
            'status': 'failed',
            'message': 'Mail failed!'}
        return jsonify(responseObject)
def generate_encrypted_auth_token(payload, priv_key):
    try:
        auth_token = jwt.encode(
             payload,
             priv_key,
             algorithm='RS512'
        )
        return auth_token
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
    except jwt.ExpiredSignatureError:
        return 'Signature expired. Please log in again.'
    except jwt.InvalidTokenError:
        return 'Invalid token. Please log in again.'

#@token_login_bp.route('/token/getotp', methods=['POST'])
#def get_otp():
#    return generate_one_time_password()

@token_login_bp.route('/token/gettoken', methods=['POST'])
def get_token():
    '''        
     curl -X POST -d '{"username": "admin", "password": "admin", "domain": "itc", "otp": "3376"}'  \
     -H "Content-Type: Application/json"  localhost:5001/token/gettoken
     '''
    privkey = current_app.config.get('private_key')
    if request.method == 'POST':
        if 'username' in request.json and 'password' in request.json and 'domain' in request.json:
            username = request.json['username']
            password = request.json['password']
            domain = request.json['domain']
            if username is None or password is None or domain is None:
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
            user_from_db = user.to_dict()
            if not user_from_db['wfc']['org'] == domain:
                responseObject = {
                    'status': 'Incorrect domain name',
                    'message': 'domain name not found against this user',}
                return jsonify(responseObject )
            else:
                org = Organization.query.filter_by(name=domain).first()
                svcs = ServiceCatalog.query.all()
                service_catalog = {}
                for s in svcs:
                    service_catalog[s.name]=s.to_dict()
                if not org.to_dict['orgtype'] == 'internal':
                    if 'otp' in request.json:
                        otp = request.json['otp']
                        otpwd = Otp.query.filter_by(otp=otp).first()
                        otpdet = otpwd.to_dict()
                        creation_date = otpdet['creation_date']
                        if otpwd is not None and otpdet['userid']==user_from_db['id'] and datetime.datetime.utcnow() - creation_date <= 10:
    #                   ldap authentication goes here
                            try:
                                conn = ldap.initialize(app.config['LDAP_PROVIDER_URL'])
                                conn.simple_bind_s(
                        'cn=%s,ou=Users,dc=test,dc=tspbillldap,dc=itc' % username, password
                                )
                                payload = {
                                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=0, seconds=3600),
                                'iat': datetime.datetime.utcnow(),
                                'sub': user_from_db
                                }
                                auth_token = generate_encrypted_auth_token(payload, privkey)
                                responseObject = {
                                        'status': 'success',
                                        'message': 'success',
                                        'auth_token': auth_token.decode(),
                                        'service_catalog': service_catalog}
                                return make_response(jsonify(responseObject)), 201
                            except ldap.INVALID_CREDENTIALS:
                                responseObject = {
                                    'status': 'Invalid credentials',
                                    'message': 'Username or password not found',}
                                return jsonify(responseObject )    
                        else:
                            responseObject = {
                                'status': 'Incorrect OTP',
                                'message': 'OTP not found',}
                            return jsonify(responseObject )
                    else:
                        otp = generate_one_time_password(user_from_db['id'])
                        return make_response(otp)
                else:                        
                    if user.check_password(password):
                            payload = {
                                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=0, seconds=3600),
                                'iat': datetime.datetime.utcnow(),
                                'sub': user_from_db
                                }
                            auth_token = generate_encrypted_auth_token(payload, privkey)
                            responseObject = {
                                    'status': 'success',
                                    'message': 'success',
                                    'auth_token': auth_token.decode(),
                                    'service_catalog': service_catalog}
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
# nbf: �Not before� time that identifies the time before which the JWT must not be accepted for processing
# iat: �Issued at� time, in Unix time, at which the token was issued
# jti: JWT ID claim provides a unique identifier for the JWT
# 
# '''
