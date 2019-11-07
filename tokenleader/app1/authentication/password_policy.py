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
        self.num_of_failed_attempt = int(policy_config.get("num_of_failed_attempt", 4))

    def create_user_with_pwd(self, UserModelClass):
        #record = User(username=cname, email=email, roles=valid_role_objects, wfc=wfc, created_by=created_by)
        pass


    def set_password(self, username, new_pwd, old_password=None,
                     initial=False, force_change=False, disable_policy=False,):
        ''' OLD PASSWORD CAN BE NONE ONLY WHEN INITIAL IS TRUE, ELSE OLD PASSWORD IS MUST
        DURING INITIAL PASSWORD , OLD PASSWORD IS NOT REQUIRED
        IGNORE FORCE CHANGE WHEN USER IS CHANGING THE PASSWORD
        SET THE PASSWORD ONCE OLD PASSWORD AUTHENTICATION IS DONE AND PASSWORD POLICY IS CHECKED
        '''
        result = False
        #OLD PASSWORD CAN BE NONE ONLY WHEN INITIAL IS TRUE, ELSE OLD PASSWORD IS MUST
        if initial is False and  old_password is None:
            raise exc.PwdSetWihoutOldPasswordError
        if  disable_policy is False and initial is False:
            #IGNORE FORCE CHANGE WHEN USER IS CHANGING THE PASSWORD
            self.authenticate_with_password(username, old_password, ignore_forece_change=True)
            #DURING INITIAL PASSWORD , OLD PASSWORD IS NOT REQUIRED  
            result = self._validate_password_while_saving(username, new_pwd)
        elif  disable_policy is False and initial is True:
            result = self._validate_password_while_saving(username, new_pwd, initial=True)
        else: 
            result = True #TODO: WE SHOULD HAVE EXCEPTION HERE INSTEAD OF TRUE
        #SET THE PASSWORD ONCE OLD PASSWORD AUTHENTICATION IS DONE AND PASSWORD POLICY IS CHECKED
        if result is True:
            password_hash = generate_password_hash(new_pwd)
            new_password = Pwdhistory(password_hash = password_hash)
            user_fm_db = self._get_userObj_from_db(username)
            user_fm_db.pwdhistory.append(new_password)
            user_fm_db.force_pwd_change = "N"
            if force_change:
                user_fm_db.force_pwd_change = "Y"
            result = self._db_commit("password_saving_failed", user_fm_db)
        return result


    def authenticate_with_password(self, username, new_pwd, ignore_forece_change=False, test=False):
        '''test=True to consider expiry time settings as seconds
        ignore_force_change=True while authentication is called from set_password method'''
        result = False
        user_fm_db = self._get_userObj_from_db(username)
        self._check_active(username)
        if test is True:
            self._check_pwd_expiry(username, count_seconds=True)
        else:
            self._check_pwd_expiry(username)
        if len(user_fm_db.pwdhistory) > 0:
            last_pwd_rec = user_fm_db.pwdhistory[-1]
            pwd_hash = last_pwd_rec.password_hash
        else: pwd_hash = ''
        if user_fm_db.num_of_failed_attempt:
            num_of_failed_attempt = user_fm_db.num_of_failed_attempt
        else:
            num_of_failed_attempt = 0
        if ( check_password_hash(pwd_hash, new_pwd) and
             num_of_failed_attempt < self.num_of_failed_attempt ):
            if (user_fm_db.force_pwd_change and 
                user_fm_db.force_pwd_change == "N" or
                ignore_forece_change):
                result = True
                user_fm_db.num_of_failed_attempt = 0
                user_fm_db.last_logged_in = datetime.datetime.utcnow()
                self._db_commit("reset_failed_attempt", user_fm_db)
            else:
                raise exc.PwdNotChangedByFirstLoginError
        elif num_of_failed_attempt > self.num_of_failed_attempt:
            self._lock_account(username)
            self._db_commit("lock_user", user_fm_db)
            raise exc.PwdWrongAttemptBeyondLimitError(self.num_of_failed_attempt)
        else:
            user_fm_db.num_of_failed_attempt = num_of_failed_attempt + 1
            self._db_commit("increase_the_failed_attempt", user_fm_db)
            remaining_attempt = self.num_of_failed_attempt - user_fm_db.num_of_failed_attempt
            raise exc.AuthenticationFailureError(remaining_attempt)
        return result


    def _validate_password_while_saving(self, username, new_pwd, initial=False):
        ''' history check is not required  when initial=True'''
        self.username = username
        self.pwd = new_pwd
        self._check_length(self.pwd)
        self._check_special_chars()
        self._check_numeric_chars()
        self._check_upper_case()
        self._check_lower_case()
        if initial is False:
            self._check_history(self.username , self.pwd)
        result = True
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
        if len(user_fm_db.pwdhistory) > 0:
            last_pwd_rec = user_fm_db.pwdhistory[-1]
            creation_date= last_pwd_rec.pwd_creation_date
        else:
            creation_date = user_fm_db.creation_date
        current_date = datetime.datetime.utcnow()
        expiry_value = self.pwd_expiry_days*3600*24
        grace_value = self.pwd_grace_period*3600*24
        #FOR TESTING ONLY CONSIDER THE NUMBERS IN CONF FILE AS SECONDS
        if count_seconds:
            expiry_value = self.pwd_expiry_days
            grace_value = self.pwd_grace_period
        elapsed_seconds = (current_date - creation_date).total_seconds()
        total_expiry_setting = expiry_value + grace_value
        if expiry_value < elapsed_seconds < total_expiry_setting:
            raise exc.PwdExpiryError(grace_period=self.pwd_grace_period)
        elif elapsed_seconds > total_expiry_setting:
            #SHOULD I CALL LOCK ACCOUNT HERE ?
            self._lock_account(username)
            raise exc.PwdExpiredAccountLockedError()
        return False, elapsed_seconds


    def _check_wrong_attempt(self):
        pass


    def _check_active(self, username):
        result = False
        user_fm_db = self._get_userObj_from_db(username)
        if isinstance(user_fm_db, User):
            if user_fm_db.is_active == "Y":
                result = True
            else:
                raise exc.UserIsDeactivatedError
        else:
            raise exc.UserNotRegisteredError
        return result


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


    def unlock_account(self, username):
        user_fm_db = self._get_userObj_from_db(username)
        user_fm_db.is_active = "Y"
        user_fm_db.num_of_failed_attempt = 0
        self._db_commit("failed_to_activate_user", user_fm_db)


    def _check_last_login(self):
        pass


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


    def _db_commit(self, status_on_fail, user_fm_db):
        try:
            db.session.commit()
            status = user_fm_db
        except Exception as e:
            print (e)
            status = {"status": ("DB_failure_%s" %status_on_fail), "message": e}
            db.session.rollback()
            raise Exception
        return status