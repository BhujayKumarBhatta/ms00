from flask import request, Blueprint, jsonify, current_app,make_response
import jwt
import datetime
import requests
import json
import random
from ldap3 import Server, Connection, ALL
#from sqlalchemy.sql import func
from tokenleader.app1 import db
from tokenleader.app1.authentication.models import User, Organization, Otp
from tokenleader.app1.catalog.models_catalog import ServiceCatalog
from builtins import None, True
from flask.globals import request
from pip._internal import req
from pip._vendor.html5lib._inputstream import non_bmp_invalid_codepoints
import email
# from flask.globals import session


token_login_bp = Blueprint('token_login_bp', __name__)

# don't try to access it here to avoid RuntimeError: Working outside of application context
#publickey = current_app.config.get('public_key') 

class Authenticator():
    
    STATUS = None
    USERNAME = None
    PASSWORD = None
    OTP = None
    EMAIL = None
    ORG = None
    OTP_MODE=None
    
    def __init__(self, request):
        self._extract_n_validate_data_from_request(request)        
                    
        if 'tokenexpiration' in current_app.config:
            tokenexpiration = current_app.config['tokenexpiration']
        else:
            tokenexpiration = 30        
        privkey = current_app.config.get('private_key')
#         user_fm_db = self.
    
    def _extract_n_validate_data_from_request(self, request):
        ''' each input also to be validated for its type and length and special character'''
        if request.method == 'POST':            
            if 'username' in request.json and \
              len(request.json['username']) <= 50 :
                self.USERNAME = request.json['username']
            if 'password' in request.json:
                self.PASSWORD = request.json['password']
            if 'domain' in request.json:
                self.ORG = request.json['domain']   # change domain key as org
            if 'otp' in request.json:
                self.OTP = request.json['otp']
            if 'email' in request.json:
                self.EMAIL=request.json['email']  
                              
    def service_catalog(self):
        svcs = ServiceCatalog.query.all()
        service_catalog = {}
        for s in svcs:
            service_catalog[s.name]=s.to_dict()
        return service_catalog
    
#     def _validate_request(self):
#         # check pair of data in request and return True/False/Issue
#         if ('username', 'otp') in request.json and not ('password','email') in request.json:
#             return True
#         elif ('username', 'password', 'domain') in request.json and not ('otp','email') in request.json:
#             return True
#         elif ('email', 'otp') in request.json and not ('password','username') in request.json:
#             return True
#         else:
#             return False
        
    def _fetch_usrinfo_fm_db(self, validuser):
        if validuser is not None:
            user_from_db = validuser.to_dict()
            # print(user_from_db)
            return user_from_db
        else:
            responseObject = {
                'status': 'failed',
                'message': 'User not registered',}
            return jsonify(responseObject )

    def get_user_info_from_db_byusername(self): 
        '''use memcahe '''
        validuser  = User.query.filter_by(username=_self.USERNAME).first()
        return self._fetch_usrinfo_fm_db(validuser)
    
    def get_validuserobject(self): 
        '''use memcahe '''
        validuser  = User.query.filter_by(username=_self.USERNAME).first()
        return validuser
        
    def get_user_info_from_db_byemail(self):
        validuser  = User.query.filter_by(email=self.EMAIL).first()
        return self._fetch_usrinfo_fm_db(validuser)
    
    def chk_external_user(self, user_from_db):
        if not user_from_db['wfc']['org'] == self.ORG:
            responseObject = {
                'status': 'failed',
                'message': 'Incorrect domain name',}
            return jsonify(responseObject )
        org = Organization.query.filter_by(name=self.ORG).first()
        if org.to_dict()['orgtype'] == 'external':
            return True
        else:
            return False
        
    def _create_random(self):
        rand = str(random.random())
        num = rand[-4:]
        return num

    def _save_otp_in_db(self,num, userid):
        user = User.query.filter_by(id=userid).first()
        self.OTP_MODE = user.to_dict()['otp_mode']
        found = Otp.query.all()
        if found:
            lastotp = Otp.query.filter_by(is_active='Y').first()
            if lastotp:
                # print('old active otp found')
                lastotp.is_active = 'N'
                db.session.commit()
        else:
            print('no records where there in otp table')
        record = Otp(otp=num,userid=userid,delivery_method=self.OTP_MODE)
        # print(record)
        db.session.add(record)
        db.session.commit()

    def send_otp_thru_mail(self, email):


        r = requests.post(url=current_app.config['MAIL_SERVICE_URI'], data=json.dumps({'mail_to':mail_to, 'msg': "<html><body>Your OTP is <b><font color=blue>"+str(num)+"</font></b>. It is only valid for "+str(otpvalidtime)+" minutes.</body></html>"}))
        if r.status_code == 200:
            print('mail success')
            responseObject = {
                'status': 'mail success',
                'message': 'Otp has been sent to your email id: '+mail_to}
            return jsonify(responseObject )
        else:
            responseObject = {
                'status': 'failed',
                'message': r.text}
            return jsonify(responseObject)
    
    def send_otp_thru_sms(self, phno):
        return phno
        # config for sms
            
    def response_using_payload(self, user_from_db, otpdet=None):
        if otpdet is not None:
            payload = {'exp': (datetime.datetime.utcnow() + \
                               datetime.timedelta(days=0,
                                                  seconds=auth.tokenexpiration)),
                        'iat': datetime.datetime.utcnow(),
                        'sub': {**otpdet, **user_from_db}
                    }
        else:
            payload = {
                        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=0, seconds=auth.tokenexpiration),
                        'iat': datetime.datetime.utcnow(),
                        'sub': user_from_db
                    }
        auth_token = generate_encrypted_auth_token(payload, auth.privkey)
        responseObject = {
            'status': 'success',
            'message': 'success',
            'auth_token': auth_token.decode(),
            'service_catalog': auth.service_catalog()}
        return make_response(jsonify(responseObject)), 201

    def generate_one_time_password(self,userid):
        try:
            # print('generating otp')
            num = self._create_random()
            self._save_otp_in_db(num, userid)
            user = User.query.filter_by(id=userid).first()
            user_from_db = user.to_dict()
            org = user_from_db['wfc']['org']
            if org in current_app.config['otpvalidfortsp']:
                otpvalidtime = current_app.config['otpvalidfortsp'][org]
            else:
                otpvalidtime = 10
            mail_to = user_from_db['email']
            phno = '5656565653'
            if self.OTP_MODE == 'mail':
                self.send_otp_thru_mail(email)
            elif self.OTP_MODE == 'sms':
                self.send_otp_thru_sms(phno)
            elif self.OTP_MODE == 'both':
                self.send_otp_thru_mail(email)
                self.send_otp_thru_sms(phno)
            else:
                return 'No mail id or phone no. is available'
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
        

@token_login_bp.route('/token/gettoken', methods=['POST'])
def get_token():
    '''        
     curl -X POST -d '{"username": "admin", "password": "admin", "domain": "itc", "otp": "3376"}'  \
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
    auth = Authenticator(request)    
#     isvalidrequest =auth._validate_request(request)
#     if isvalidrequest is True:
    # CASE 1: Username & Otp        
    if auth.USERNAME is not None:
        user_from_db = auth.get_user_info_from_db_byusername()
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
        if org in current_app.config['otpvalidfortsp']:
            otpvalidtime = current_app.config['otpvalidfortsp'][org]
        else:
            otpvalidtime = 10
        if otpwd is not None and otpdet['is_active']== 'Y' and otpdet['userid']==user_from_db['id'] and (datetime.datetime.utcnow()-creation_date).total_seconds()/60.0 <= otpvalidtime:
            try:                   
                # ------ payload to put in seperate function ------                    
                return auth.response_using_payload(user_from_db, otpdet)
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
    # Case 2: Username & Password
    if auth.USERNAME is None or auth.PASSWORD is None:
        responseObject = {
            'status': 'missing authentication info ',
            'message': 'no authentication information provided',}
        return jsonify(responseObject)
    user_from_db = auth.get_user_info_from_db_byusername()
    if auth.chk_external_user(user_from_db) is True:
        if auth.ldap_auth() is True:
            otp = auth.generate_one_time_password(user_from_db['id'])
            return make_response(otp)
    else:
        validuser = auth.get_validuserobject()
        if validuser.check_password(auth.PASSWORD):
            return auth.response_using_payload(user_from_db)
        else:
            responseObject = {
                'status': 'failed',
                'message': 'Password did not match',}
            return jsonify(responseObject)
    # Case 3: Email & Otp
    if auth.EMAIL is not None or auth.OTP is not None:
        user_from_db = auth.get_user_info_from_db_byemail()
            if user_from_db['allowemaillogin'] == 'Y':
                otpwd = Otp.query.filter_by(otp=otp).first()
                if otpwd:
                    otpdet = otpwd.to_dict()
                    creation_date = otpdet['creation_date']
                    otpdet['creation_date'] = str(otpdet['creation_date'])
                    org = user_from_db['wfc']['org']
                    if org in current_app.config['otpvalidfortsp']:
                        otpvalidtime = current_app.config['otpvalidfortsp'][org]
                    else:
                        otpvalidtime = 10
                if otpwd is not None and otpdet['is_active']== 'Y' and otpdet['userid']==user_from_db['id'] and (datetime.datetime.utcnow()-creation_date).total_seconds()/60.0 <= otpvalidtime:
                    return auth.response_using_payload(user_from_db, otpdet)
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
# else:
#     responseObject = {
#         'status': 'restricted',
#         'message': 'invalid request',}
#     return jsonify(responseObject)


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
