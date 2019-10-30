import json


class TLException(Exception):
    status = "UNKNOWN_STATUS"
    message = "Unknown status"

    def __init__(self, status=None, message=None):
        if status:  self.status = status
        if message: self.message = message
        self.ret_val = {"status": self.status, "message": self.message }
        super(TLException, self).__init__(self.status, self.message)

    def __str__(self):
        return json.dumps(self.ret_val)


    def __repr__(self):
        return self.ret_val


class InvalidInputForNameError(TLException):
    status = "InvalidInputForNameError"
    message = ("Incorrect Username has been entered, must be"
               "text within 40 caharacter and doesn't use "
               "these characters '!#$%^&*()<>?\/\|}{~:'")
    
class NoUserIdentifierInputError(TLException):
    status = "NoUserIdentifierInputError"
    message = ("either 'username' or 'email'  is required for login")



class InvalidInputForEmailError(TLException):
    status = "InvalidInputForEmailError"
    message = ("Incorrect email has been entered, must be"
               "text within 40 caharacter")


class InvalidInputForPWDError(TLException):
    status = "InvalidInputForPWDError"
    message = ("Incorrect password input, must be"
               "text within 15 caharacter")


class InvalidInputForDomainError(TLException):
    status = "InvalidInputForDomainError"
    message = ("Incorrect password input, must be"
               "text within 15 caharacter")


class InvalidInputForOTPError(TLException):
    status = "InvalidInputForOTPError"
    message = ("Incorrect OTP input, must be"
               "4 digit number")


class DomainConfigurationError(TLException):
    status = "DomainConfigurationError"
    message = ("domain has not been configured"
               " in tokenleader_configs by administrator ")


class DomainValidationError(TLException):
    status = "Domain_Error"
    message = ("Domain Doesn't match with the users"
               " record")


class AuthenticationFailureError(TLException):
    status = "AuthenticationFailure"
    message = "Authentication Failure"


class PasswordVerificationError(TLException):
    status = "PasswordVerificationError"
    message = "wrong password supplied"


class UserNotRegisteredError(TLException):
    status = "UserNotRegistered"
    message = "User not registered"


class AuthBackendConfigError(TLException):
    status = "AuthBackendConfigError"
    message = ("auth backend  mentioned in tokenleader_config "
               "has  not been implemented ")


class MissingAuthInfoError(TLException):
    status = "MissingAuthInfoError"
    message = ("no authentication information , e.g "
               "username, email, domain and/or OTP  has been"
               "provided")


class IncorrectOtpError(TLException):
    status = "IncorrectOtpError"
    message = ("Incorrect OTP, check the otp in your mail "
               "or sms and  reenter the correct OTP")


class OTPExpiredError(TLException):
    status = "OTPExpiredError"
    message = ("OTP Expired, re login and enter the OTP within the time"
               "validity time shown after login. You may contact administrator "
               " to request increasing the expiry time, if needed")


class OTPGenerationError(TLException):
    status = "OTPGenerationError"
    message = "OTPGenerationError"


class TokenleaderPrivateKeyNotFoundError(TLException):
    status = "TokenleaderPrivateKeyNotFoundError"
    message = "RSA Private Key configuration error in the server"   


class KafkaServerConfigError(TLException):
    status = "KafkaServerConfigError"
    message = "Kafka server not configured in tokenleader_configs"



class PasswordLengthError(TLException):
    status = "PasswordLengthError"
    def __init__(self, pwd_length_min, pwd_length_max):
        self.pwd_length_min = pwd_length_min
        self.pwd_length_max = pwd_length_max
        self.message = ("Password minimum  length should be %d and max length"
            "within %d" %(self.pwd_length_min, self.pwd_length_max))
        super(PasswordLengthError, self).__init__(self.status, self.message)


class PwdWithoutSpecialCharError(TLException):
    status = "PwdWithoutSpecialCharError"
    message = "Password must have at least one special character"
    

class PwdWithoutNumberError(TLException):
    status = "PwdWithoutNumberError"
    message = "Password must have at least one numeric character"
    
    
class PwdWithoutAlphabetError(TLException):
    status = "PwdWithoutAlphabetError"
    message = "Password must have at least one  character from Alphabet"


class PwdWithoutUpperCaseError(TLException):
    status = "PwdWithoutUpperCaseError"
    message = "Password must have at least one  upper case character"
    
    
class PwdHistroyCheckError(TLException):
    status = "PwdHistroyCheckError"
    message = "Last N number of password can not be used"



# def checkme(a, b):
#     if a==b:
#         print("OK")
#     else:
#         raise SException
# 
# try:
#     checkme(1,2)
# except Exception as e:
#     print("only e:", e)
#     print("repr:", e.__repr__())
#     print(type(e))
#