import json
import jwt
import requests
import random
import datetime
from ldap3 import Server, Connection, ALL
from tokenleader.app1 import db
from tokenleader.app1.authentication.models import User, Organization, Otp
from tokenleader.app1.catalog.models_catalog import ServiceCatalog
from flask import jsonify, make_response, current_app
import re



class TokenManager():
    '''    
    1. user to supply domin name (or treat it as defualt in absense)
    2. read the yml and retrieve  the auth_backend and OTP_REQUIRED 
    3. retrieve user info from auth_backend 
    4. 
    '''
    def __init__(self, user_dict_fm_db):
        self.user_dict_fm_db = user_dict_fm_db
        
    def get_token_or_otp(self, request):
        auth = Authenticator(request)
        print("auth.STATUS: ", auth.STATUS)
        
        if not auth.STATUS:    
            responseObject = {
                'status': 'failed',
                'message': 'Incorrect data format',}
            return jsonify(responseObject)
        else:
            if auth.USERNAME is None or auth.PASSWORD is None:
                responseObject = {
                    'status': 'missing authentication info ',
                    'message': 'no authentication information provided',}
                return jsonify(responseObject)
    #        print('correct request format')
            user_from_auth_backend = auth.get_user_fm_auth_backend()
            print(user_from_auth_backend)
            payload = {
                                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=0, seconds=auth.tokenexpiration),
                                'iat': datetime.datetime.utcnow(),
                                'sub': user_from_auth_backend
                            }
            print("OTP required: %s , authentication status: %s"
                  %(auth.OTP_REQUIRED, auth.AUTHENTICATION_STATUS))
            if auth.AUTHENTICATION_STATUS is False:
                responseObject = {
                    'status': 'failed',
                    'message': 'Authentication Failure'}
                return jsonify(responseObject)
            elif auth.OTP_REQUIRED :
    #            print(user_from_auth_backend['id'])
                print("trigerring otp")
                otp = auth.generate_one_time_password(user_from_auth_backend['id'])
                return make_response(otp)
            else:
                auth_token = self.generate_encrypted_auth_token(payload, auth.privkey)
                responseObject = {
                    'status': 'success',
                    'message': 'success',
                    'auth_token': auth_token.decode(),
                    'service_catalog': auth.service_catalog()}
                return make_response(jsonify(responseObject)), 201            

    def get_token_by_otp(self, request):
        auth = Authenticator(request)
        if not auth.STATUS:
            responseObject = {
                'status': 'failed',
                'message': 'Incorrect data format',}
            return jsonify(responseObject)
        else:
            if auth.USERNAME is not None:
                validuser = auth.get_validuserobject()
                if validuser is None:
                    responseObject = {
                        'status': 'failed',
                        'message': 'User not registered',}
                    return jsonify(responseObject )
                user_from_db = auth.get_user_fm_auth_backend_after_authentication()
            else:
                responseObject = {
                    'status': 'missing authentication info ',
                    'message': 'no authentication information provided',}
                return jsonify(responseObject)
            if auth.OTP is not None:
                otpwd = Otp.query.filter_by(otp=auth.OTP).first()
                if otpwd:
                    otpdet = otpwd.to_dict()
                    creation_date = otpdet['creation_date']
                    otpdet['creation_date'] = str(otpdet['creation_date'])
                org = user_from_db['wfc']['org']
                if org in current_app.config['otp']:
                    otpvalidtime = current_app.config['otp'][org]
                else:
                    otpvalidtime = 10
                if otpwd is not None and otpdet['is_active']== 'Y' and otpdet['userid']==user_from_db['id'] and (datetime.datetime.utcnow()-creation_date).total_seconds()/60.0 <= otpvalidtime:
                    try:                   
                        # ------ payload to put in seperate function ------                    
                        payload = {'exp': (datetime.datetime.utcnow() + \
                                            datetime.timedelta(days=0,
                                                                seconds=auth.tokenexpiration)),
                                'iat': datetime.datetime.utcnow(),
                                'sub': {**otpdet, **user_from_db}
                            }
                        auth_token = self.generate_encrypted_auth_token(payload, auth.privkey)
                        responseObject = {
                            'status': 'success',
                            'message': 'success',
                            'auth_token': auth_token.decode(),  
                            'service_catalog': auth.service_catalog()}
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
            
    def gettoken_by_email_otp(self, request):
        auth = Authenticator(request)
        if not auth.STATUS:
            responseObject = {
                'status': 'failed',
                'message': 'Incorrect data format',}
            return jsonify(responseObject)
        else:
            if auth.EMAIL is not None or auth.OTP is not None:
                user_from_db = auth.get_user_fm_auth_backend_after_authentication()
                if user_from_db['allowemaillogin'] == 'Y':
                    otpwd = Otp.query.filter_by(otp=auth.OTP).first()
                    if otpwd:
                        otpdet = otpwd.to_dict()
                        creation_date = otpdet['creation_date']
                        otpdet['creation_date'] = str(otpdet['creation_date'])
                        org = user_from_db['wfc']['org']
                        if org in current_app.config['otp']:
                            otpvalidtime = current_app.config['otp'][org]
                        else:
                            otpvalidtime = 10
                    if otpwd is not None and otpdet['is_active']== 'Y' and otpdet['userid']==user_from_db['id'] and (datetime.datetime.utcnow()-creation_date).total_seconds()/60.0 <= otpvalidtime:
                        payload = {
                                    'exp': datetime.datetime.utcnow() + datetime.timedelta(days=0, seconds=auth.tokenexpiration),
                                    'iat': datetime.datetime.utcnow(),
                                    'sub': {**user_from_db, **otpdet}
                                }
                        auth_token = self.generate_encrypted_auth_token(payload, auth.privkey)
                        responseObject = {
                            'status': 'success',
                            'message': 'success',
                            'auth_token': auth_token.decode(),
                            'service_catalog': auth.service_catalog()}
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
                    'status': 'missing authentication info ',
                    'message': 'no authentication information provided',}
                return jsonify(responseObject)
    
    def generate_encrypted_auth_token(self, payload, priv_key):
#         print(payload)
#         print(priv_key)
        try:
            auth_token = jwt.encode(
                 payload,
                 priv_key,
                 algorithm='RS512'
            )
            return auth_token
        except Exception as e:
            return e
                        
    def decrypt_n_verify_token(self, auth_token, pub_key):
#         print(pub_key)
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

   


