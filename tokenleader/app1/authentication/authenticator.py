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
from tokenleader.app1.authentication.otp import Otpmanager
from tokenleader.app1.authentication.tokenmanager import TokenManager
from tokenleader.app1 import exceptions as exc


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
        self.request = request      
        self.AUTHENTICATION_STATUS = False
        self.USERNAME = None
        self.PASSWORD = None
        self.OTP = None
        self.EMAIL = None
        self.ORG = 'default'
        self.OTP_MODE=None

        self.AUTH_BACKEND = None
        self.BACKEND_CONFIGS = None
        self.OTP_REQUIRED = True

        self.domain_validtion_status = False
        self.password_authenticate = False
        self.user_dict  = {}


    def  authenticate(self):
        try:
            self._extract_data_from_request(self.request)
            self._get_userdict_fm_auth_backend()
            self._get_domain_configs_from_yml()
            tokenmgr = TokenManager(self.userObj)
            otpmgr = Otpmanager(self.userObj)
            if self.OTP :
                otpmgr.validate_otp(self.OTP)
                result = tokenmgr.get_token()
            else:
                self._validate_users_domain_name()
                self._password_authenticate()
                if self.OTP_REQUIRED == True:
                    result= otpmgr.despatch_otp()
                else:
                    result = tokenmgr.get_token()
        except Exception as auth_exception_erro_status:
            result = auth_exception_erro_status.__repr__()
            print(result)
        return result


    def _extract_data_from_request(self, request):       
        regex = re.compile('[@_!#$%^&*()<>?/\|}{~:]')
        pwdregex = re.compile('[_!#$%^&*()<>?/\|}{~:]')
        
        if 'username' in request.json:
            if ( len(request.json['username']) <= 40 and 
                 regex.search(request.json['username']) is None and
                 isinstance(request.json['username'], str)):
                self.USERNAME = request.json['username']
        else:
            raise exc.InvalidInputForNameError
        
        if 'password' in request.json: 
            if (len(request.json['password']) <=15 and
                pwdregex.search(request.json['password']) is None and
                isinstance(request.json['password'], str)):
                self.PASSWORD = request.json['password']
            else:
                raise exc.InvalidInputForPWDError
                
        if 'domain' in request.json:
            if (len(request.json['domain']) <=10 and 
                regex.search(request.json['domain']) is None and
                isinstance(request.json['domain'], str)):
                self.ORG = request.json['domain']
            else:
                raise exc.InvalidInputForDomainError
            
        if 'otp' in request.json:
            if (len(request.json['otp']) == 4 and
                regex.search(request.json['otp']) is None and
                isinstance(request.json['otp'], str)):
                self.OTP = request.json['otp']
            else:
                raise exc.InvalidInputForOTPError
            
        if 'email' in request.json:
            if (len(request.json['email']) <= 40 and 
                pwdregex.search(request.json['email']) is None and
                isinstance(request.json['email'], str)):
                self.EMAIL=request.json['email']
            else:
                raise exc.InvalidInputForEmailError
            
        result = (self.USERNAME, self.PASSWORD, self.OTP, self.EMAIL, self.ORG )
        return result


    def _get_domain_configs_from_yml(self):
        ''' doc string '''        
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
                    raise exc.AuthBackendConfigError
                msg = ("OTP requried status: %s for domain: %s"
                            %(self.OTP_REQUIRED , self.ORG))
                break
            else:
                raise exc.DomainConfigurationError
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
            print("got a authbackend: %s  in tokenelader_configs"
                  " which is not implemented" %self.AUTH_BACKEND)
#             raise exc.AuthBackendConfigError
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
                raise exc.MissingAuthInfoError
            if user_from_db:
                user_dict = user_from_db.to_dict()
                self.user_dict = user_dict
                self.userObj = user_from_db
                status = True
                msg = "found a valid user in database"
            else:
                raise exc.UserNotRegisteredError 
            result = {"status": status, "user_dict": self.user_dict, 
                  "userObj": user_from_db, "message": msg}          
        except Exception as e:
            result = e
        print(result)
        return result


    def _validate_users_domain_name(self):
        users_domain_from_db = self.user_dict.get('wfc').get('org')
        if self.ORG == users_domain_from_db:
            self.domain_validtion_status = True
        else:
            raise  exc.DomainValidationError
        return self.domain_validtion_status


    def _password_authenticate(self):
        if self.userObj.check_password(self.PASSWORD):
            self.password_authenticate = True
        else:
            raise exc.PasswordVerificationError
        return self.password_authenticate


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
   