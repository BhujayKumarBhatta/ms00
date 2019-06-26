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


class Authenticator():

    ''' 1. move this class to a different module( auth_class.py )file
    2.  get_token and verify token to be  api routes to be in auth_routes.py 
    3.  dont use ldap only for authentication and dont consider all user info shd be in local db.
        user to provide org name ( if not provided it is taken as 'default' )
        based on user provided orgtype , search config yml what is its auth_backend 
        retrieve the user from that auth_backend (currenty it always  retrieves it from
        local db is a  design problem
        for org type default -  user is retrived from local
    4. rectify   the error as suggested by pylint hints  underlined as blue or red , 
       remove leading and trailing white space , too long lines , uppercase cinstant names etc'''


    STATUS = None
    USERNAME = None
    PASSWORD = None
    OTP = None
    EMAIL = None
    ORG = 'default'
    OTP_MODE=None
    tokenexpiration=30
    privkey=None

    def __init__(self, request):
        self._extract_n_validate_data_from_request(request)
        print(current_app.config['tokenexpiration'])
        if 'tokenexpiration' in current_app.config:
            self.tokenexpiration = current_app.config['tokenexpiration']
        self.privkey = current_app.config.get('private_key')

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

    def get_auth_backend_from_yml(self):
        domain_list = current_app.config.get('domains')
        if self.ORG  in domain_list:
            for d in domain_list:
                if d.get('auth_backend') == 'default':
                    pass
                elif d.get('auth_backend') == 'ldap':
                    ldap_attribs =  {'ldap_host': 1,
                                   'ldap_port': 2,
                                   'ldap_version': 3, 
                                   'OU': 4,
                                   'O': 5, 
                                   'DC': 6}
                elif d.get('auth_backend') == 'active_directory':
                    pass
                elif d.get('auth_backend') == 'sqldb':
                    pass
                else:
                    msg = " unconfigured auth_backend"
                    status = False
        else:
            msg = ("% domain has not been configured in  tokenleader_configs"
                   " by administrator" %self.ORG)
            status = False
        return_value = {'status': status, 'msg': msg}
        return return_value


    def get_user_info_from_db_byusername(self):
        '''use memcahe '''
        validuser  = User.query.filter_by(username=self.USERNAME).first()
        return self._fetch_usrinfo_fm_db(validuser)

    def get_user_info_from_db_byemail(self):
        validuser  = User.query.filter_by(email=self.EMAIL).first()
        return self._fetch_usrinfo_fm_db(validuser)

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

    def get_validuserobject(self): 
        '''use memcahe '''
        validuser  = User.query.filter_by(username=self.USERNAME).first()
        return validuser

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
#         print(record)
        db.session.add(record)
        db.session.commit()

    def send_otp_thru_mail(self, email, num, otpvalidtime):
#         print('check mail')  
#         print(email, num, otpvalidtime)      
        msg = ("<html><body>Your OTP is <b><font color=blue>"+ \
               str(num)+"</font></b>. It is only valid for "+ \
               str(otpvalidtime)+" minutes.</body></html>")
        r = requests.post(url=current_app.config['MAIL_SERVICE_URI'], 
                          data=json.dumps({'mail_to':email, 'msg': msg}))
        if r.status_code == 200:
            print('mail success')
            responseObject = {
                'status': 'mail success',
                'message': 'Otp has been sent to your email id: '+email }
            return jsonify(responseObject )
        else:
            responseObject = {
                'status': 'failed',
                'message': r.text}
            return jsonify(responseObject)

    def send_otp_thru_sms(self, phno):
        return phno
        # config for sms

    def ldap_auth(self):
        s = Server(current_app.config['ldap']['Server'], 
                   port=current_app.config['ldap']['Port'], 
                   get_info=ALL)
        username = 'cn={0},ou=Users,dc=test,dc=tspbillldap,dc=itc'.format(self.USERNAME)
        c = Connection(s, 
                       user=self.USERNAME, 
                       password=self.PASSWORD)
        if not c.bind():#            
            return True
        else:
            return False

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
#             phno = '5656565653'
            if self.OTP_MODE == 'mail':
#                 print('mode mail')
                return self.send_otp_thru_mail(mail_to, num, otpvalidtime)
#             elif self.OTP_MODE == 'sms':
#                 self.send_otp_thru_sms(phno, num, otpvalidtime)
#             elif self.OTP_MODE == 'both':
#                 self.send_otp_thru_mail(mail_to, num, otpvalidtime)
#                 self.send_otp_thru_sms(phno)
            else:
                return 'No mail id or phone no. is available'
        except Exception as e:
            return e
    def service_catalog(self):
        svcs = ServiceCatalog.query.all()
        service_catalog = {}
        for s in svcs:
            service_catalog[s.name]=s.to_dict()
        return service_catalog



class TokenManager():
    def gettoken_by_usr_pwd(self, request):
        auth = Authenticator(request)
        if auth.USERNAME is None or auth.PASSWORD is None:
            responseObject = {
                'status': 'missing authentication info ',
                'message': 'no authentication information provided',}
            return jsonify(responseObject)
        validuser = auth.get_validuserobject()
        if validuser is None:
                responseObject = {
                    'status': 'failed',
                    'message': 'User not registered',}
                return jsonify(responseObject )
        user_from_db = auth.get_user_info_from_db_byusername()
        if auth.chk_external_user(user_from_db) is True:
            if auth.ldap_auth() is True:
                otp = auth.generate_one_time_password(user_from_db['id'])
                return make_response(otp)
            else:
                responseObject = {
                    'status': 'failed',
                    'message': 'Password did not match',}
                return jsonify(responseObject)
        else:
            if validuser.check_password(auth.PASSWORD):
                payload = {
                            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=0, seconds=auth.tokenexpiration),
                            'iat': datetime.datetime.utcnow(),
                            'sub': user_from_db
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
                    'message': 'Password did not match',}
                return jsonify(responseObject)

    def gettoken_byusr_otp(self, request):
        auth = Authenticator(request)  
        if auth.USERNAME is not None:
            validuser = auth.get_validuserobject()
            if validuser is None:
                responseObject = {
                    'status': 'failed',
                    'message': 'User not registered',}
                return jsonify(responseObject )
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
        if auth.EMAIL is not None or auth.OTP is not None:
            user_from_db = auth.get_user_info_from_db_byemail()
            if user_from_db['allowemaillogin'] == 'Y':
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
        print(payload)
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

   


# def response_using_payload(self, user_from_db, otpdet=None):
#         if otpdet is not None:
#             payload = {'exp': (datetime.datetime.utcnow() + \
#                                datetime.timedelta(days=0,
#                                                   seconds=self.tokenexpiration)),
#                         'iat': datetime.datetime.utcnow(),
#                         'sub': {**otpdet, **user_from_db}
#                     }
#         else:
#             payload = {
#                         'exp': str(datetime.datetime.utcnow() + datetime.timedelta(days=0, seconds=self.tokenexpiration)),
#                         'iat': str(datetime.datetime.utcnow()),
#                         'sub': user_from_db
#                     }
# #         print(payload)
#         auth_token = generate_encrypted_auth_token(payload, self.privkey)
#         responseObject = {
#             'status': 'success',
#             'message': 'success',
#             'auth_token': auth_token.decode(),
#             'service_catalog': self.service_catalog()}
#         return make_response(jsonify(responseObject)), 201
