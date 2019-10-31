import os
import datetime
import logging
import re
from tokenleader.app1 import db
from tokenleader.app1.authentication.models import User, Pwdhistory
from tokenleader.app1 import exceptions as exc
from werkzeug.security import generate_password_hash, check_password_hash

logger = logging.getLogger(__name__)


class Pwdpolicy:

    def __init__(self, policy_config={}, pwd=None):
        self.policy_config = policy_config
        self.pwd_length_min = policy_config.get("pwd_length_min", 7)
        self.pwd_length_max = policy_config.get("pwd_length_max", 50)
        self.pwd = pwd
        self.num_of_old_pwd_blocked = policy_config.get("num_of_old_pwd_blocked", 3)


    def validate_password(self, pwd):
        self.pwd = pwd
        try:
            self._check_length(pwd)          
            self._check_special_chars()
            self._check_numeric_chars()
            self._check_upper_case()            
            self._check_lower_case()
            result = True
        except Exception as err:
            result = err
        return result


    def _check_length(self, pwd):
        if (len(pwd) >= self.pwd_length_min and 
            len(pwd) <= self.pwd_length_max):
            result = True
        else:
            raise exc.PasswordLengthError(pwd_length_min=self.pwd_length_min, 
                                          pwd_length_max=self.pwd_length_max)
        return  result


    def _check_special_chars(self):
        regex_special_chars = re.compile('[@!#$%^&*()<>?/\|}{~:]')
        if regex_special_chars.search(self.pwd) is not  None:
            result = True
        else:
            raise exc.PwdWithoutSpecialCharError
        return result


    def _check_numeric_chars(self):
        regex_numeric = re.compile('[0-9]')
        if regex_numeric.search(self.pwd) is not  None:
            result = True
        else:
            raise exc.PwdWithoutNumberError
        return result


    def _check_lower_case(self):
        regex_lower_case = re.compile('[a-z]')
        if regex_lower_case.search(self.pwd) is not  None:
            result = True
        else:
            raise exc.PwdWithoutAlphabetError
        return result


    def _check_upper_case(self):
        regex_upper_case = re.compile('[A-Z]')
        if regex_upper_case.search(self.pwd) is not  None:
            result = True
        else:
            raise exc.PwdWithoutUpperCaseError
        return  result


    def _check_expiry(self):
        pass


    def _check_history(self, username, new_pwd):
        user_fm_db = User.query.filter_by(username=username).first()
        order = int(self.num_of_old_pwd_blocked)
        last_3_pwdhist = user_fm_db.pwdhistory[-order:]
        for pwdhist in last_3_pwdhist:
            if check_password_hash(pwdhist.password_hash, new_pwd):
                raise exc.PwdHistroyCheckError
                break
        return True


    def set_password(self, username, new_pwd): 
        password_hash = generate_password_hash(new_pwd)   
        new_password = Pwdhistory(password_hash = password_hash)
        user_fm_db = User.query.filter_by(username=username).first()
        user_fm_db.pwdhistory.append(new_password)
        try:
            db.session.commit()
            status = user_fm_db
        except Exception as e:
            print (e)
            status = {"status": "password_saving_failed", "message": e}
            db.session.rollback()
        return status



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

    