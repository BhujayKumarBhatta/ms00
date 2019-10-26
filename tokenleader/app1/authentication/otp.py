import json
import requests
import random
import datetime
from tokenleader.app1 import db
from tokenleader.app1.authentication.models import  Otp
from flask import jsonify, make_response, current_app
from  tokenleader.app1.kafka import kafka_producer as kp
from tokenleaderclient.rbac.wfc import WorkFuncContext
from tokenleader.app1 import exceptions as exc
from tokenleader.app1.utils import common_utils


class Otpmanager():

    '''    
    1. send otp to user
    3.if otp is already present in the request, check otp validity
    
    '''

    def __init__(self, userObj_fm_db):
        self.userObj_fm_db = userObj_fm_db
        self.userdict_fm_db = userObj_fm_db.to_dict()
        self.otpvalidtime = 60
        self.userid_db = self.userdict_fm_db.get('username')
        self.email_db = self.userdict_fm_db.get('email')
        self.OTP_MODE = self.userdict_fm_db.get('otp_mode')
        self.existing_otp = None
        if userObj_fm_db.otp:                
            self.existing_otp = userObj_fm_db.otp.otp
        self.OTP_Validation_status = False


    def despatch_otp(self):
        reloaded_conf = common_utils.reload_configs()
        rand = str(random.random())
        num = rand[-4:]
        if self._save_otp_in_db(num) is True:
            org = self.userdict_fm_db.get('wfc').get('org')
            if org in reloaded_conf.get('otp') and reloaded_conf.get('otp').get(org):
                otpvalidtime = reloaded_conf.get('otp').get(org)
                self.otpvalidtime = otpvalidtime
            else:
                otpvalidtime =  self.otpvalidtime
            mail_to = self.userdict_fm_db.get('email')
            sms_to = self.userdict_fm_db.get('mobile_num')
            kafka_response = {'status': 'OTP_SENT', "otp": num,
                              "otp_sending_method": self.OTP_MODE,
                              "mail_to": mail_to, "sms_to": sms_to,
                              'message': ("OTP: %s with validity: %s" 
                                          %(str(num), otpvalidtime)),}

            conf = {"kafka_servers": current_app.config.get("kafka_servers")}
            kp.notify_kafka(conf, self._get_wfc(), 
                                "topic_tokenleader", kafka_response)

            if self.OTP_MODE == "show":
                message =  ('OTP: %s SENT to %s with %s seconds validity'
                            %(self.OTP_MODE, str(otpvalidtime), num))
            message =  ('OTP SENT to %s with %s seconds validity'
                        %(self.OTP_MODE, str(otpvalidtime)))
            response = {'status': 'OTP_SENT', 'message': message }
        else:
            raise exc.OTPGenerationError(message=self._save_otp_in_db(num))
        return response


    def validate_otp(self, otp_input):
        reloaded_conf = common_utils.reload_configs()
        creation_date = self.userObj_fm_db.otp.creation_date
        current_date = datetime.datetime.utcnow()
        org_fm_db = self.userdict_fm_db.get('wfc').get('org')
        otp_fm_db = self.userObj_fm_db.otp.otp
        if org_fm_db in reloaded_conf.get('otp'):
            otpvalidtime = reloaded_conf.get('otp').get(org_fm_db)
        else:
            otpvalidtime = self.otpvalidtime
            print("otp expiry for the domain %s not configured ,"
                  " failing back to default" %org_fm_db)
        elapsed_time = (current_date-creation_date).total_seconds()/60.0
        print("time detials", elapsed_time, otpvalidtime)
        if elapsed_time <= otpvalidtime:
            if  otp_input == otp_fm_db:
                self.OTP_Validation_status = True
            else:
                raise exc.IncorrectOtpError
        else:
            raise exc.OTPExpiredError
        return self.OTP_Validation_status


    def _get_wfc(self):
        wfc = WorkFuncContext()
        wfc.setcontext(self.userid_db, self.email_db, self.userdict_fm_db)
        return wfc


    def _save_otp_in_db(self, num):
        ''' 
        otp is backref to user so that we get user.otp
        not storing the old otp records to reduce database load'''
        try:
            if self.existing_otp:
                print('updating the existing otp :%s by newotp: %s'
                      %(self.existing_otp, num))
                self.userObj_fm_db.otp.otp = num
                db.session.commit()
            else:
                print('adding a newe otp in otp table')
                new_otp = Otp(otp=num, delivery_method=self.OTP_MODE) 
                self.userObj_fm_db.otp  =   new_otp
#                 db.session.add(new_otp)
                db.session.commit()
            status = True
        except Exception as e:
            print (e)
            status = {"status": "OTPGeneratonFiled", "message": e}
            db.session.rollback()        
        return status
    
    
    


