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

    def __init__(self, policy_config={}, username=None, pwd=None):
        self.userObj_fm_db = None
        self.pwd = pwd
        self.username = username
        self.policy_config = policy_config
        self.pwd_length_min = int(policy_config.get("pwd_length_min", 7))
        self.pwd_length_max = int(policy_config.get("pwd_length_max", 50))
        self.num_of_old_pwd_blocked = int(policy_config.get("num_of_old_pwd_blocked", 3))
        self.pwd_expiry_days = int(policy_config.get("pwd_expiry_days", 90))
        self.pwd_grace_period = int(policy_config.get("pwd_grace_period", 7))


    def set_password(self, username, new_pwd):
        result = self._validate_password_while_saving(username, new_pwd)
        if result is True:
            password_hash = generate_password_hash(new_pwd)
            new_password = Pwdhistory(password_hash = password_hash)
            user_fm_db = self._get_userObj_from_db(username)
            user_fm_db.pwdhistory.append(new_password)
            try:
                db.session.commit()
                result = user_fm_db
            except Exception as e:
                print (e)
                result = {"status": "password_saving_failed", "message": e}
                db.session.rollback()
        return result


    def authenticate_with_password(self, username, new_pwd):
        '''1. user account is active 
        2. check password_expiry
        3. compare pwd digest 
        '''
        user_fm_db = self._get_userObj_from_db(username)
        if isinstance(user_fm_db, User):
            if user_fm_db.is_active == "Y":
                last_pwd_rec = user_fm_db.pwdhistory[-1]
                pwd_hash = last_pwd_rec.password_hash
                if check_password_hash(pwd_hash, new_pwd):
                    result = True
                else:
                    #check number os failed attempt
                    #if count is greater than conf lock account
                    #increase the number os failed attempt
                    
                    raise exc.AuthenticationFailureError
            else:
                raise exc.UserIsDeactivatedError
        else:
            raise exc.UserNotRegisteredError
        return result

    def _validate_password_while_saving(self, username, new_pwd):
        self.username = username
        self.pwd = new_pwd
        try:
            self._check_length(self.pwd)
            self._check_special_chars()
            self._check_numeric_chars()
            self._check_upper_case()
            self._check_lower_case()
            self._check_history(self.username , self.pwd)
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


    def _check_history(self, username, new_pwd):
        user_fm_db = self._get_userObj_from_db(username)
        order = int(self.num_of_old_pwd_blocked)
        last_3_pwdhist = user_fm_db.pwdhistory[-order:]
        for pwdhist in last_3_pwdhist:
            if check_password_hash(pwdhist.password_hash, new_pwd):
                raise exc.PwdHistroyCheckError
                break
        return True


    def _check_pwd_expiry(self, username, count_seconds=None):
        user_fm_db = self._get_userObj_from_db(username)
        last_pwd_rec = user_fm_db.pwdhistory[-1]
        current_date = datetime.datetime.now()
        creation_date= last_pwd_rec.pwd_creation_date
        expiry_value = self.pwd_expiry_days*3600*24
        grace_value = self.pwd_grace_period*3600*24
        #FOR TESTING ONLY CONSIDER THE NUMBERS IN CONF FILE AS SECONDS
        if count_seconds:
            expiry_value = self.pwd_expiry_days
            grace_value = self.pwd_grace_period
        elapsed_seconds = (current_date - creation_date).total_seconds()
        if elapsed_seconds in range(expiry_value, (expiry_value + grace_value)):
            raise exc.PwdExpiryError(grace_period=self.pwd_grace_period)
        elif elapsed_seconds > (expiry_value + grace_value):
            #SHOULD I CALL LOCK ACCOUNT HERE ?
            self._lock_account(username)
            raise exc.PwdExpiredAccountLockedError()
        return False, elapsed_seconds


#     def _lock_pwd_on_pwd_expiry(self, username, count_seconds=None):
#         try:
#             exp_result = self._check_pwd_expiry(username)
#             if count_seconds:
#                 exp_result = self._check_pwd_expiry(username, count_seconds=True)
#         except Exception as e:
#             exp_result = e
#             if  exp_result  and exp_result.status == "PwdExpiredAccountLockedError":
#                 self._lock_account(username)
#                 raise exc.PwdExpiredAccountLockedError
#         return False


    def _check_wrong_attempt(self):
        pass


    def _check_active(self):
        pass


    def _check_last_login(self):
        pass


    def _record_wrong_attempt(self):
        pass


    def _lock_account(self, username):
        user_fm_db = self._get_userObj_from_db(username)
        user_fm_db.is_active = "N"
        try:
            db.session.commit()
            status = user_fm_db
        except Exception as e:
            print (e)
            status = {"status": "failed_to_deactivate_user", "message": e}
            db.session.rollback()
            raise Exception


    def unlock_account(self):
        user_fm_db = self._get_userObj_from_db(username)
        user_fm_db.is_active = "Y"
        try:
            db.session.commit()
            status = user_fm_db
        except Exception as e:
            print (e)
            status = {"status": "failed_to_activate_user", "message": e}
            db.session.rollback()
            raise Exception


    def _lock_dormant(self):
        pass


    def _get_userObj_from_db(self, username=None, email=None):
        uOb = self.userObj_fm_db
        if uOb and  (uOb.username ==  username or uOb.email == email):
            user_fm_db = uOb
        else:
            if username:
                user_fm_db = User.query.filter_by(username=username).first()
            elif email:
                user_fm_db = User.query.filter_by(email=email).first()
            elif username and email:
                user_fm_db = User.query.filter_by(email=email).first()
            else:
                user_fm_db = None
            self.userObj_fm_db = user_fm_db
        return user_fm_db

    