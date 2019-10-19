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
from builtins import False


class Authenticator():

    '''    
    1. user to supply domin name (or treat it as defualt in absense)
    2. read the yml and retrieve  the auth_backend and OTP_REQUIRED 
    3. retrieve user info from auth_backend 
    4. authenticate with the backend
    
    4.  dont use ldap only for authentication and dont consider all user info shd be in local db.
        user to provide org name ( if not provided it is taken as 'default' )
        based on user provided orgtype , search config yml what is its auth_backend 
        retrieve the user from that auth_backend (currenty it always  retrieves it from
        local db is a  design problem
        for org type default -  user is retrived from local
    '''

    def __init__(self, request):        
        self.tokenexpiration=30
        self.privkey=None
#         print(current_app.config.get('token').get('tokenexpiration'))
        if 'tokenexpiration' in current_app.config.get('token'):
            self.tokenexpiration = current_app.config.get('token').get('tokenexpiration')
        self.privkey = current_app.config.get('private_key')


    def  authenticate(self, request):
        msg = ""
        self._extract_data_from_request(request)
        self._get_userdict_fm_auth_backend()
        self._get_domain_configs_from_yml()
        self._validate_users_domain_name()
        if self.domain_validtion_status == True
            self._password_authenticate()
            if  self.AUTHENTICATION_STATUS:
                msg = ("authentication  successful ")
            else:
                msg = ("authentication  failed ")
        else:
            msg = ("Wrong domain name: ", self.ORG)
            self.AUTHENTICATION_STATUS = False
        result = {'status': self.AUTHENTICATION_STATUS, 'message': msg,}
        print(result)
        return self.AUTHENTICATION_STATUS
    
    
    def _extract_data_from_request(self, request):
        self.USERNAME = None
        self.PASSWORD = None
        self.OTP = None
        self.EMAIL = None
        self.ORG = 'default'
        self.OTP_MODE=None
        regex = re.compile('[@_!#$%^&*()<>?/\|}{~:]')
        pwdregex = re.compile('[_!#$%^&*()<>?/\|}{~:]')
        if ('username' in request.json and 
            len(request.json['username']) <= 40 and 
            regex.search(request.json['username']) is None and
            isinstance(request.json['username'], str)):
            self.USERNAME = request.json['username']
        if ('password' in request.json and
            len(request.json['password']) <=15 and 
            pwdregex.search(request.json['password']) is None and
            isinstance(request.json['password'], str)):
            self.PASSWORD = request.json['password']
        if ('domain' in request.json and
            len(request.json['domain']) <=10 and 
            regex.search(request.json['domain']) is None and
            isinstance(request.json['domain'], str)):
            self.ORG = request.json['domain']
            #TODO: change domain key as org
        if ('otp' in request.json and
            len(request.json['otp']) == 4 and
            regex.search(request.json['otp']) is None and
            isinstance(request.json['otp'], str)):
            self.OTP = request.json['otp']
        if ('email' in request.json and
            len(request.json['email']) <= 40 and 
            pwdregex.search(request.json['email']) is None and
            isinstance(request.json['email'], str)):
            self.EMAIL=request.json['email']
        result = (self.USERNAME, self.PASSWORD, self.OTP, self.EMAIL, self.ORG )
        return result


    def _get_domain_configs_from_yml(self):
        ''' doc string '''
        self.AUTH_BACKEND = None
        self.BACKEND_CONFIGS = None
        self.OTP_REQUIRED = True
        domain_list = current_app.config.get('domains')
        for domain_dict in domain_list:
            if self.ORG  in domain_dict:
                print("found settings for domain: ", self.ORG )
                domain_settings = domain_dict.get(self.ORG)
                if domain_settings.get('auth_backend') == 'default':
                    self.AUTH_BACKEND = 'default'
                    self.BACKEND_CONFIGS = 'default'
                    self.OTP_REQUIRED = domain_settings.get('otp_required')
                elif domain_settings.get('auth_backend') == 'ldap':
                    self.AUTH_BACKEND = 'ldap'
                    self.BACKEND_CONFIGS =  self._get_ldap_backend_configs(domain_settings)
                    self.OTP_REQUIRED = domain_settings.get('otp_required')
                else:
                    msg = " unconfigured auth_backend"
                    print(msg)
                msg = ("OTP requried status: %s for domain: %s"
                            %(self.OTP_REQUIRED , self.ORG))
                break
            else:
                msg = ("%s domain has not been configured in  tokenleader_configs"
                       " by administrator , ask admin to insert this domain in"
                       " tokenleader_configs" %self.ORG)
        result = (self.AUTH_BACKEND, self.BACKEND_CONFIGS, self.OTP_REQUIRED)
        print(result)
        return result


    def _get_userdict_fm_auth_backend(self):
        ''' doc string'''
        if self.AUTH_BACKEND == 'default':
            if self.USERNAME:
                user_fm_backend = self._get_user_dict_from_default_db(user=self.USERNAME)
            elif self.EMAIL:
                user_fm_backend = self._get_user_dict_from_default_db(email=self.EMAIL)
            else:
                pass
        elif self.AUTH_BACKEND == 'ldap':
            user_fm_backend = self._get_usr_info_fm_ldap()
#            print('ldap:'+str(user_fm_backend))
        else:
            user_fm_backend = {'status': 'failed', 
                               'message':'{0} domain has not been configured'
                               ' in  tokenleader_configs by administrator'.format(self.ORG)}
#            print('default:'+str(user_fm_backend))
#        print(user_fm_backend)
        return user_fm_backend


    def _get_ldap_backend_configs(self, domain_settings):
        ldap_backend_settings = {'ldap_host': domain_settings.get('ldap_host'),
           'ldap_port': domain_settings.get('ldap_port'),
           'ldap_version': domain_settings.get('ldap_version'), 
           'OU': domain_settings.get('OU'),
           'O': domain_settings.get('O'),
           'DC1': domain_settings.get('DC1'),
           'DC2': domain_settings.get('DC2'),
           'DC3': domain_settings.get('DC3')}
        return ldap_backend_settings


    def _get_user_dict_from_default_db(self, user=None, email=None):
        '''use memcahe '''
        status = False
        self.user_dict  = {}
        msg = ""
        try:
            if user and not email:  
                user_from_db  = User.query.filter_by(username=user).first()
            elif email and not user:
                user_from_db = User.query.filter_by(email=email).first()
            elif user and email:
                user_from_db  = User.query.filter_by(username=user).first()
            else:
                user_from_db = None                
                msg = ("either user or email is required for login")
            if user_from_db:                
                user_dict = user_from_db.to_dict()
                self.user_dict = user_dict
                self.userObj = user_from_db
                status = True
                msg = "found a valid user in database"
            else:
                msg = "User not registered"            
        except Exception as e:            
            msg = e
        result = {"status": status, "user_dict": self.user_dict, 
                  "userObj": user_from_db, "message": msg}
        
        print(result)
        return self.user_dict


    def _validate_users_domain_name(self):        
        users_domain_from_db = self.user_dict.get('wfc').get('org')
        self.domain_validtion_status = True if self.ORG == users_domain_from_db else False              
        return self.domain_validtion_status
    
    
    def _password_authenticate(self):
        self.password_authenticate = False
        if self.userObj.check_password(self.PASSWORD):
            self.password_authenticate = True
        else:
            print("password authentication with backend failed")
        return self.password_authenticate
            
                
                
            
    
        
        
        
    
   
        

    

     
    def generate_one_time_password(self,userid):
        try:
            # print('generating otp')
            num = self._create_random()
#            print(userid)
            self._save_otp_in_db(num, userid)
            user = User.query.filter_by(id=userid).first()
            user_from_db = user.to_dict()
            org = user_from_db['wfc']['org']
            if org in current_app.config['otp']:
                otpvalidtime = current_app.config['otp'][org]
            else:
                otpvalidtime = 10
            print("OTP: %s with validity: %s" %(str(num), otpvalidtime))
            mail_to = user_from_db['email']
#             phno = '5656565653'
            if self.OTP_MODE == 'mail':
#                print('mode mail')
                return self.send_otp_thru_mail(mail_to, num, otpvalidtime)
#             elif self.OTP_MODE == 'sms':
#                 self.send_otp_thru_sms(phno, num, otpvalidtime)
#             elif self.OTP_MODE == 'both':
#                 self.send_otp_thru_mail(mail_to, num, otpvalidtime)
#                 self.send_otp_thru_sms(phno)
            else:
                  responseObject = {'status': 'failed',
                            'message': 'No OTP mode mentioned for this user.'}
                  print(responseObject)
                  return jsonify(responseObject)
        except Exception as e:
            print(e)
            return e 
     
    def service_catalog(self):
        svcs = ServiceCatalog.query.all()
        service_catalog = {}
        for s in svcs:
            service_catalog[s.name]=s.to_dict()
        return service_catalog
            
    
            
        
        #Once user object is available
        #We check if OTP is available and return user
        #else We check passowrd return user   
        if self.OTP:
            result = self._convert_user_to_dict(user_from_db)
        else:
            if user_from_db:
                
                if user_from_db.check_password(self.PASSWORD):
                    result = self._convert_user_to_dict(user_from_db)
                    self.AUTHENTICATION_STATUS = True
                else:
                    
                    # print(result)
            else:
                result = {
                    'status': 'failed',
                    'message': 'User not registered',}
                
        return result

            
    def get_validuserobject(self): 
        '''use memcahe '''
        validuser  = User.query.filter_by(username=self.USERNAME).first()
        return validuser
        
    def _create_random(self):
        rand = str(random.random())
        num = rand[-4:]
        return num

    def _save_otp_in_db(self,num, userid):
        try:
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
#            print(record)
            db.session.add(record)
            db.session.commit()
            return True
        except Exception as e:
            return e
            
    def send_otp_thru_mail(self, email, num, otpvalidtime):
#         print('check mail')  
#         print(email, num, otpvalidtime)      
        msg = ("<html><body>Your OTP is <b><font color=blue>"+ \
               str(num)+"</font></b>. It is only valid for "+ \
               str(otpvalidtime)+" minutes.</body></html>")
        r = requests.post(url=current_app.config['MAIL_SERVICE_URI'], 
                          data=json.dumps({'mail_to':email, 'msg': msg}))
        print(r)
        # print(r.status_code)
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
        return phno       #TODO: config for sms

    def _get_usr_info_fm_ldap(self):
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
        ldap_config = self.BACKEND_CONFIGS 
        conn = Server(ldap_config['ldap_host'], 
                       port=ldap_config['ldap_port'],
                       #system user , password , dc etc will be required
                       get_info=ALL)
        uinfo = "ou="+ldap_config['OU']+","+"dc="+ldap_config['DC1']+\
                ","+"dc="+ldap_config['DC2']+","+"dc="+ldap_config['DC3']
        if self._bind_to_ldap(conn, uinfo) is True:
            return self._get_user_info_from_default_db(user=self.USERNAME)
            #Todo: the user detials to come from ldap
        else:
#            print('Fail')
            responseObject = {
                'status': 'failed',
                'message': 'Authentication Failure'}
            return jsonify(responseObject)
 
    def _bind_to_ldap(self, conn, uinfo):
        uinfo = 'cn={0},{1}'.format(self.USERNAME, uinfo)
        c = Connection(conn, 
                       user=uinfo, 
                       password=self.PASSWORD)
        if  c.bind():
            self.AUTHENTICATION_STATUS = True
            return True            
        else:
        	self.AUTHENTICATION_STATUS = False
        	return False


    



class TokenManager():
    '''    
    1. user to supply domin name (or treat it as defualt in absense)
    2. read the yml and retrieve  the auth_backend and OTP_REQUIRED 
    3. retrieve user info from auth_backend 
    4. 
    '''
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
