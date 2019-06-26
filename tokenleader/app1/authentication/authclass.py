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

    def _get_auth_backend_from_yml(self):
        ''' doc string '''
        auth_backend = 'default'
        domain_list = current_app.config.get('domains')
        print(current_app.config)
        if self.ORG in current_app.config.get('typeoftsp'):
            self.ORG = 'tsp'
        if self.ORG  in domain_list:
            for domain_name in domain_list:
                if domain_name.get('auth_backend') == 'default':
                    auth_backend = 'default'
                elif domain_name.get('auth_backend') == 'ldap':
                    backend_configs =  {'ldap_host': domain_name.get('ldap_host'),
                                   'ldap_port': domain_name.get('ldap_port'),
                                   'ldap_version': domain_name.get('ldap_version'), 
                                   'OU': domain_name.get('OU'),
                                   'O': domain_name.get('O'),
                                   'DC1': domain_name.get('DC1'),
                                   'DC2': domain_name.get('DC2'),
                                   'DC3': domain_name.get('DC3')}
                    auth_backend = 'ldap'
                    
                elif domain_name.get('auth_backend') == 'active_directory':
                    pass
                elif domain_name.get('auth_backend') == 'sqldb':
                    pass
                else:
                    msg = " unconfigured auth_backend"
                    status = False
        else:
            msg = ("% domain has not been configured in  tokenleader_configs"
                   " by administrator" %self.ORG)
            status = False
        return_value = {'status': status, 'msg': msg, 'auth_backend': auth_backend,
                        'backend_configs': backend_configs}
        return return_value

    def get_user_fm_auth_backend(self):
        ''' doc string'''
        result = self._get_auth_backend_from_yml()
        if result.get('auth_backend') == 'default':
            if self.USERNAME:
                user_fm_backend = self.get_user_info_from_default_db(user=self.USERNAME)
            elif self.USERNAME:
                user_fm_backend = self.get_user_info_from_default_db(email=self.EMAIL)
            else:
                pass
        elif result.get('auth_backend') == 'ldap':
            user_fm_backend = self.get_usr_info_fm_ldap()
        else:
            pass
        return user_fm_backend

    def get_user_info_from_default_db(self, user=None, email=None):
        '''use memcahe '''
        if user and not email:  
            user_from_db  = User.query.filter_by(username=user).first()
        elif email and not user:
            user_from_db = User.query.filter_by(email=email).first()
        elif user and email:
            user_from_db  = User.query.filter_by(username=user).first()
        else:
            result = ("either user or email is required for login")
        result = self._convert_user_to_dict(user_from_db)
        return result

    def _convert_user_to_dict(self, qry_result):
        if qry_result:
            user_to_dict = qry_result.to_dict()
            # print(user_from_db)
            return user_to_dict
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

    def get_usr_info_fm_ldap(self):
        '''        
         #     user_fm_ldap = "ldap searach "
            # else:
            #     user_fm_ldap = ("no user is found in ldap ")                
            # if ('role', 'department .... wfc realted ') not in user_fm_ldap:
            #     pass
            #     "call the local db to get those info "            
            # return user_fm_ldap 
        '''
        #TODO: research on open ldap to find user details
        result = self._get_auth_backend_from_yml()
        ldap_config = result.get('backend_configs') 
        conn = Server(ldap_config['ldap_host'], 
                       port=ldap_config['ldap_port'],
                       #system user , password , dc etc will be required
                       get_info=ALL)
        uinfo = "ou="+ldap_config['OU']+","+"dc="+ldap_config['DC1']+\
                ","+"dc="+ldap_config['DC2']+","+"dc="+ldap_config['DC2']
        print(uinfo)
        if self.ldap_auth(conn, uinfo) is True:
            return self.get_user_info_from_default_db(user=self.USERNAME)
        else:
            responseObject = {
                'status': 'failed',
                'message': 'Password did not match',}
            return jsonify(responseObject)
                  

    def ldap_auth(self, conn, uinfo):
        uinfo = 'cn={0},{1}'.format(self.USERNAME, uinfo)
        c = Connection(conn, 
                       user=uinfo, 
                       password=self.PASSWORD)
        if not c.bind():            
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
        user_from_db = auth.get_user_info_from_default_db(user=auth.USERNAME)
        if auth.chk_external_user(user_from_db) is True:
            if not auth.get_usr_info_fm_ldap()['status'] == 'failed':
                if 'id' in auth.get_usr_info_fm_ldap():
                    otp = auth.generate_one_time_password(auth.get_usr_info_fm_ldap()['id'])
                    return make_response(otp)
                else:
                    return 'something went wrong'
            else:
                # Password did not
                return auth.get_usr_info_fm_ldap()
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
            user_from_db = auth.get_user_info_from_default_db(user=auth.USERNAME)
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
            user_from_db = auth.get_user_info_from_default_db(email=auth.EMAIL)
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
