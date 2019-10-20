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
        self.AUTHENTICATION_STATUS = False


    def  authenticate(self, request):
        msg = ""
        self._extract_data_from_request(request)
        self._get_userdict_fm_auth_backend()
        self._get_domain_configs_from_yml()
        self._validate_users_domain_name()
        if self.domain_validtion_status == True:
            self._password_authenticate()
            if  self.AUTHENTICATION_STATUS:
                msg = ("authentication  successful ")
            else:
                msg = ("authentication  failed ")
        else:
            msg = ("Wrong domain name: ", self.ORG)
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
            
   