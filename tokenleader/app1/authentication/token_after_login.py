from flask import request, Blueprint, jsonify, current_app,make_response
import jwt
import datetime
import requests
import json
import random
from ldap3 import Server, Connection, ALL
#from sqlalchemy.sql import func
from tokenleader.app1 import db, app
from tokenleader.app1.authentication.models import User, Organization, Otp
from tokenleader.app1.catalog.models_catalog import ServiceCatalog
# from flask.globals import session


token_login_bp = Blueprint('token_login_bp', __name__)

# don't try to access it here to avoid RuntimeError: Working outside of application context
#publickey = current_app.config.get('public_key') 

def generate_one_time_password(userid):
    try:
        # print('generating otp')
        rand = str(random.random())
        num = rand[-4:]
        found = Otp.query.all()
        if found:
            lastotp = Otp.query.filter_by(is_active='Y').first()
            if lastotp:
                # print('old active otp found')
                lastotp.is_active = 'N'
                db.session.commit()
        else:
            print('no records where there in otp table')
        record = Otp(otp=num,userid=userid)
        # print(record)
        db.session.add(record)
        db.session.commit()
        user = User.query.filter_by(id=userid).first()
        user_from_db = user.to_dict()
        org = user_from_db['wfc']['org']
        otpvalidtime = app.config['otpvalidfortsp'][org]
        mail_to = user_from_db['email']
        r = requests.post(url=app.config['MAIL_SERVICE_URI'], data=json.dumps({'mail_to':mail_to, 'msg': "<html><body>Your OTP is <b><font color=blue>"+str(num)+"</font></b>. It is only valid for "+str(otpvalidtime)+" minutes.</body></html>"}))
        if r.status_code == 200:
            print('mail success')
            responseObject = {
                'status': 'mail success',
                'message': 'Otp has been sent to your email id: '+mail_to}
            return jsonify(responseObject )
        else:
            responseObject = {
                'status': 'failed',
                'message': e}
            return jsonify(responseObject)
    except Exception as e:
        return e
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
#        print(str(request.json))
        if 'username' in request.json and 'otp' in request.json:
#            print('username & otp found')
            username = request.json['username']
#            print(username)
            if username is not None:
                user = User.query.filter_by(username=username).first()
                if user is not None:
                    user_from_db = user.to_dict()
                    # print(user_from_db)
                else:
                    responseObject = {
                        'status': 'failed',
                        'message': 'User not registered',}
                    return jsonify(responseObject )
            else:
                responseObject = {
                    'status': 'missing authentication info ',
                    'message': 'no authentication information provided',}
                return jsonify(responseObject)
            otp = request.json['otp']
            # print(otp)
            if otp is not None:
                otpwd = Otp.query.filter_by(otp=otp).first()
                if otpwd:
                    otpdet = otpwd.to_dict()
                    creation_date = otpdet['creation_date']
                    otpdet['creation_date'] = str(otpdet['creation_date'])
                org = user_from_db['wfc']['org']
                otpvalidtime = app.config['otpvalidfortsp'][org]
                # print(otpvalidtime)
                # print('current time              ', 'otp creation time  	', 'time diff       ')
                # print(datetime.datetime.utcnow(),creation_date,datetime.datetime.utcnow()-creation_date)
                if otpwd is not None and otpdet['is_active']== 'Y' and otpdet['userid']==user_from_db['id'] and (datetime.datetime.utcnow()-creation_date).total_seconds()/60.0 <= otpvalidtime:
                    try:
                        svcs = ServiceCatalog.query.all()
                        service_catalog = {}
                        for s in svcs:
                            service_catalog[s.name]=s.to_dict()                                
                        payload = {
                            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=0, seconds=3600),
                            'iat': datetime.datetime.utcnow(),
                            'sub': {**otpdet, **user_from_db}
                        }
                        # print(otpdet)
                        # print(payload)
                        auth_token = generate_encrypted_auth_token(payload, privkey)
                        # print(auth_token)
                        responseObject = {
                            'status': 'success',
                            'message': 'success',
                            'auth_token': auth_token.decode(),
                            'service_catalog': service_catalog}
                        return make_response(jsonify(responseObject)), 201
                    except Exception as e:
                        responseObject = {
                            'status': 'failed',
                            'message': e,}
                        return jsonify(responseObject )
                else:
                    responseObject = {
                        'status': 'failed',
                        'message': 'Incorrect OTP',}
                    return jsonify(responseObject )
            else:
                responseObject = {
                    'status': 'failed',
                    'message': 'OTP is required',}
                return jsonify(responseObject )
        if 'username' in request.json and 'password' in request.json:
            username = request.json['username']
#            print(username)
            password = request.json['password']
#            print(password)
            if username is None or password is None:
                responseObject = {
                    'status': 'missing authentication info ',
                    'message': 'no authentication information provided',}
                return jsonify(responseObject)
            user = User.query.filter_by(username=username).first()
            if user is None:
                responseObject = {
                    'status': 'failed',
                    'message': 'User not registered',}
                return jsonify(responseObject )
            user_from_db = user.to_dict()
            if 'domain' in request.json:
                if request.json['domain'] is not None and not user_from_db['wfc']['org'] == str(request.json['domain']).strip():
                    responseObject = {
                        'status': 'failed',
                        'message': 'Incorrect domain name',}
                    return jsonify(responseObject )
#                print('domain is in request')
                org = Organization.query.filter_by(name=request.json['domain']).first()
            else:
#                print('domain not in request')
                org = Organization.query.filter_by(name=user_from_db['wfc']['org']).first()
            svcs = ServiceCatalog.query.all()
            service_catalog = {}
            for s in svcs:
                service_catalog[s.name]=s.to_dict()
            if not org.to_dict()['orgtype'] == 'internal':
#                    print('incase of external domain')
                s = Server(app.config['ldap']['Server'], port=app.config['ldap']['Port'], get_info=ALL)
                username = 'cn={0},ou=Users,dc=test,dc=tspbillldap,dc=itc'.format(username)
                c = Connection(s, user=username, password=password)
                if not c.bind():
                    responseObject = {
                        'status': 'failed',
                        'message': 'Invalid Credential',}
                    return jsonify(responseObject)
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
                        'status': 'failed',
                        'message': 'Password did not match',}
                    return jsonify(responseObject)
        if 'email' in request.json and 'otp' in request.json:
            email = request.json['email']
            otp = request.json['otp']
            if email is not None or otp is not None:
                user = User.query.filter_by(email=email).first()
                if user is not None:
                    user_from_db = user.to_dict()
                    if user_from_db['allowemaillogin'] == 'Y':
                        otpwd = Otp.query.filter_by(otp=otp).first()
                        if otpwd:
                            otpdet = otpwd.to_dict()
                            creation_date = otpdet['creation_date']
                            otpdet['creation_date'] = str(otpdet['creation_date'])
                            org = user_from_db['wfc']['org']
                            otpvalidtime = app.config['otpvalidfortsp'][org]
                            # print(otpvalidtime)
                        if otpwd is not None and otpdet['is_active']== 'Y' and otpdet['userid']==user_from_db['id'] and (datetime.datetime.utcnow()-creation_date).total_seconds()/60.0 <= otpvalidtime:
                            payload = {
                                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=0, seconds=3600),
                                'iat': datetime.datetime.utcnow(),
                                'sub': {**user_from_db, **otpdet}
                            }
                            auth_token = generate_encrypted_auth_token(payload, privkey)
                            responseObject = {
                                'status': 'success',
                                'message': 'success',
                                'auth_token': auth_token.decode()}
                            return make_response(jsonify(responseObject)), 201
                        else:
                            responseObject = {
                                'status': 'failed',
                                'message': 'Incorrect OTP',}
                            return jsonify(responseObject )
                    else:
                        responseObject = {
                            'status': 'failed',
                            'message': 'Unauthorized',}
                        return make_response(jsonify(responseObject)), 401
                else:
                    responseObject = {
                        'status': 'failed',
                        'message': 'User not registered',}
                    return jsonify(responseObject )
            else:
                responseObject = {
                    'status': 'missing authentication info ',
                    'message': 'no authentication information provided',}
                return jsonify(responseObject)
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
                        'payload': payload
                     }
#                     return auth_token
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
