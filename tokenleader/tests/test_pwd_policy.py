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
        pwd_policy.validate_password(testpwd)
        try:
            result = pwd_policy._check_special_chars()
        except Exception as e:
            result = e            
        self.assertTrue(result.status == "PwdWithoutSpecialCharError")
        #CHECK PRESENSE OF SPECIAL CHARS SUCCESS
        testpwd = "12345678901#@"
        pwd_policy.validate_password(testpwd)
        try:
            result = pwd_policy._check_special_chars()
        except Exception as e:
            result = e
        self.assertTrue(result is True)
        #CAPITAL LETTER FAIL
        testpwd = "a12345678901#@"
        pwd_policy.validate_password(testpwd)
        try:
            result = pwd_policy._check_upper_case()
        except Exception as e:
            result = e
        self.assertTrue(result.status == "PwdWithoutUpperCaseError")
        #CAPITAL LETTER PASS
        testpwd = "aA12345678901#@"
        pwd_policy.validate_password(testpwd)
        try:
            result = pwd_policy._check_upper_case()
        except Exception as e:
            result = e
        self.assertTrue(result is True)
        #LOWER LETTER PASS
        testpwd = "aA12345678901#@"
        pwd_policy.validate_password(testpwd)
        try:
            result = pwd_policy._check_lower_case()
        except Exception as e:
            result = e
        self.assertTrue(result is True)
        #LOWER LETTER FAIL
        testpwd = "A12345678901#@"
        pwd_policy.validate_password(testpwd)
        try:
            result = pwd_policy._check_lower_case()
        except Exception as e:
            result = e
        self.assertTrue(result.status == "PwdWithoutAlphabetError")
        #SET PASSWORD IN THE NEW TABLE
        self.user_creation_for_test()
        pwd_policy.set_password('u1', 'password1')
        pwd_policy.set_password('u1', 'password2')
        pwd_policy.set_password('u1', 'password3')
        pwd_policy.set_password('u1', 'password4')
        #USE A PASSWWORD OLDER THAN LAST 3 AND PASS
        pwd_policy._check_history('u1', 'password1') 
        try:
            #USE A PASSWORD WOITHIN LAST LAST 3 AND FAIL
            pwd_policy._check_history('u1', 'password2')
        except Exception as e:
            self.assertTrue(e.status == "PwdHistroyCheckError")
        #EXPIARY TEST CONSIDERIG DAYS AS SECONDS
        pwd_policy._check_pwd_expiry('u1', count_seconds=True)




