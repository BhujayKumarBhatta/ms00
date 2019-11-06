import time
from tokenleader.app1.configs.testconf import conf as tconf
from tokenleader.app1.authentication.password_policy import Pwdpolicy
from unittest import TestCase
from tokenleader.tests.base_test import  BaseTestCase
from tokenleader.tests.admin_ops import TestUserModel

pwd_policy_conf = tconf.yml.get('pwdpolicy')
pwd_policy = Pwdpolicy(pwd_policy_conf)


class PTesting(TestUserModel):

    def test_pwd(self):
        #MIN FAILURE
        try:
            pwd_policy = Pwdpolicy(pwd_policy_conf, "123")
            result = pwd_policy._check_length("123")
        except Exception as e:
            result = e
        self.assertTrue(result.status == "PasswordLengthError")
        #CORRECT LENGTH PASSED
        try:
            pwd_policy = Pwdpolicy(pwd_policy_conf, "1234567")
            result = pwd_policy._check_length("1234567")
        except Exception as e:
            result = e
        self.assertTrue(result is True)
        #MORE THAN MAX FALIED
        try:
            pwd_policy = Pwdpolicy(pwd_policy_conf, "12345678901")
            result = pwd_policy._check_length("12345678901")
        except Exception as e:
            result = e
        self.assertTrue(result.status == "PasswordLengthError")
        #CHECK PRESENSE OF SPECIAL CHARS FAIL
        testpwd = "12345678901"
        pwd_policy = Pwdpolicy(pwd_policy_conf, 'u1', "12345678901")
        try:
            result = pwd_policy._check_special_chars()
        except Exception as e:
            result = e            
        self.assertTrue(result.status == "PwdWithoutSpecialCharError")
        #CHECK PRESENSE OF SPECIAL CHARS SUCCESS
        testpwd = "12345678901#@"
        pwd_policy = Pwdpolicy(pwd_policy_conf, 'u1', "12345678901#@")
        try:
            result = pwd_policy._check_special_chars()
        except Exception as e:
            result = e
        self.assertTrue(result is True)
        #CAPITAL LETTER FAIL
        testpwd = "a12345678901#@"
        pwd_policy = Pwdpolicy(pwd_policy_conf, 'u1', "a12345678901#@")        
        try:
            result = pwd_policy._check_upper_case()
        except Exception as e:
            result = e
        self.assertTrue(result.status == "PwdWithoutUpperCaseError")
        #CAPITAL LETTER PASS
        testpwd = "aA12345678901#@"
        pwd_policy = Pwdpolicy(pwd_policy_conf, 'u1', testpwd)
        try:
            result = pwd_policy._check_upper_case()
        except Exception as e:
            result = e
        self.assertTrue(result is True)
        #LOWER LETTER PASS
        testpwd = "aA12345678901#@"
        pwd_policy = Pwdpolicy(pwd_policy_conf, 'u1', testpwd)
        try:
            result = pwd_policy._check_lower_case()
        except Exception as e:
            result = e
        self.assertTrue(result is True)
        #LOWER LETTER FAIL
        testpwd = "A12345678901#@"
        pwd_policy = Pwdpolicy(pwd_policy_conf, 'u1', testpwd)
        try:
            result = pwd_policy._check_lower_case()
        except Exception as e:
            result = e
        self.assertTrue(result.status == "PwdWithoutAlphabetError")
        #SET PASSWORD IN THE NEW TABLE
        self.user_creation_for_test()
        pwd_policy.set_password('u1', 'password1', initial=True, disable_policy=True)
        pwd_policy.set_password('u1', 'password2', initial=True, disable_policy=True)
        pwd_policy.set_password('u1', 'password3', initial=True, disable_policy=True)
        pwd_policy.set_password('u1', 'password4', initial=True, disable_policy=True)
        #USE A PASSWWORD OLDER THAN LAST 3 AND PASS
        try:
            pwd_policy._check_history('u1', 'password1')
        except Exception as e:
            print(e, "this exception should not occur")
        try:
            #USE A PASSWORD WOITHIN LAST LAST 3 AND FAIL
            pwd_policy._check_history('u1', 'password2')
        except Exception as e:
            self.assertTrue(e.status == "PwdHistroyCheckError")
        #EXPIARY TEST CONSIDERING DAYS AS SECONDS that is 30+30 seconds as set in test_tokenleader_configs.yml
        try:
            #THE ELAPSED TIME IS TYPICALLY 14SEC FROM THE CREATION TIME AND HENCE
            #LESS THAN 30 SEC WHICH IS SET AS EXPIRY TIME , PASSWORD EXPIRY WILL FIND FALSE
            result, _ = pwd_policy._check_pwd_expiry('u1', count_seconds=True)
            self.assertTrue(result == False)            
            #SLEEP FOR 30 SEC SO ELAPSED TIME 14+30IS HIGHER THAN THE EXXPIRY TIME
            #BUT WITHIN THE GRACE PEROID TIME 30+30
            time.sleep(35)
            pwd_policy._check_pwd_expiry('u1', count_seconds=True)              
        except Exception as e:
            self.assertTrue(e.status == "PwdExpiryError")
        try:
            #SLEEP MORE BEYOND 60 SEC , NOW LOCK USER ON PWD EXPIARY
            time.sleep(35)
            pwd_policy._check_pwd_expiry('u1', count_seconds=True)
        except Exception as e:
            self.assertTrue(e.status == "PwdExpiredAccountLockedError")
        #WITHOUT OLD PASSWORD PASSWORD CHANGE IS NOT ALLOWED
        try:
            pwd_policy.set_password('u1', 'password10')
        except Exception as e:
            self.assertTrue(e.status == "PwdSetWihoutOldPasswordError")
        #EARLIER WE HAD SET PASSWORD AS password1, LETS TRY TO AUTHENTICATE WITH THIS
        #AND GET ACCOUNT IS LOCKED ERROR
        try:
            result = pwd_policy.authenticate_with_password('u1', 'password1')
        except Exception as e:
            self.assertTrue(e.status == "UserIsDeactivatedError")
        #LETS UNLOCK THE ACCOUNT AND TRY TO AUTHENTICATE. IT SHOULD LOCK THE ACCOUNT AGAIN
        #SINCE THE CURRENT TIME IS STILL PAST THE GRACE PERIOD
        try:
            pwd_policy.unlock_account('u1')
            result = pwd_policy.authenticate_with_password('u1', 'password1', test=True)
        except Exception as e:
            self.assertTrue(e.status == "PwdExpiredAccountLockedError")
        #UNLOCK THE ACCOUNT, RESET PWD WITH INITIAL AND LET USER TRY TO AUTHENTICATE
        try:
            pwd_policy.unlock_account('u1')
            pwd_policy.set_password('u1', 'password5', initial=True, disable_policy=True)#AT THIS STAGE WE SHOULD HAVE AN OPTION TO FORCE_CHANGE_PWD_NEXT_LOGIN
            result = pwd_policy.authenticate_with_password('u1', 'password5')
            self.assertTrue(result == True)
        except Exception as e:
            print(e, "this exception should not occur")
        #LETS ATTEMPT WRONG PWD AND SEE THE COUNTER INCREASES
        try:            
            result = pwd_policy.authenticate_with_password('u1', 'passwordwrong')
        except Exception as e:
            self.assertTrue(e.status == "AuthenticationFailure")
            self.assertTrue(pwd_policy.userObj_fm_db.num_of_failed_attempt == 1)
        #ON SUCESSFUL LOGIN THE COUNTER SHOULD RESET
        try:            
            result = pwd_policy.authenticate_with_password('u1', 'password5')
            self.assertTrue(result == True)
            self.assertTrue(pwd_policy.userObj_fm_db.num_of_failed_attempt == 0)
        except Exception as e:
            print(e, "this exception should not occur")
            
        #KEEP ATTEPMITNG WRONG TILL IT LOCKS
        try:
            result = pwd_policy.authenticate_with_password('u1', 'passwordwrong')
        except Exception as e:
            self.assertTrue(e.status == "AuthenticationFailure")
            self.assertTrue(pwd_policy.userObj_fm_db.num_of_failed_attempt == 1)
        try:            
            result = pwd_policy.authenticate_with_password('u1', 'passwordwrong')
        except Exception as e:
            self.assertTrue(e.status == "AuthenticationFailure")
            self.assertTrue(pwd_policy.userObj_fm_db.num_of_failed_attempt == 2)
        try:            
            result = pwd_policy.authenticate_with_password('u1', 'passwordwrong')
        except Exception as e:
            self.assertTrue(e.status == "AuthenticationFailure")
            self.assertTrue(pwd_policy.userObj_fm_db.num_of_failed_attempt == 3)
        try:            
            result = pwd_policy.authenticate_with_password('u1', 'password5')
        except Exception as e:
            self.assertTrue(e.status == "PwdWrongAttemptBeyondLimitError")







