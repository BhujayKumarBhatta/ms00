import os
import datetime
import logging
from tokenleader.app1 import exceptions as exc

logger = logging.getLogger(__name__)


class Pwdpolicy:

    def __init__(self, pwd, policy_config={}):
        self.pwd = pwd
        self.policy_config = policy_config
        self.pwd_length_min = policy_config.get("pwd_length_min", 7)
        self.pwd_length_max = policy_config.get("pwd_length_max", 50)



    def validate_password(self):
        try:
            self._check_length()
            result = True
        except Exception as err:
            result = err
        return result


    def _check_length(self):
        if (len(self.pwd) >= self.pwd_length_min and 
            len(self.pwd) <= self.pwd_length_max):
            result = True
        else:
            raise exc.PasswordLengthError(self.pwd_length_min, )
        return  result


    def _check_alpha_numeric_special(self):
        pass


    def _check_expiry(self):
        pass


    def _check_history(self):
        pass


    def _check_wrong_attempt(self):
        pass


    def _check_active(self):
        pass


    def _check_last_login(self):
        pass
    
    
    def _record_wrong_attempt(self):
        pass
    
    
    def _lock_account(self):
        pass


    def unlock_account(self):
        pass


    def _lock_dormant(self):
        pass
    
    
    
        
    