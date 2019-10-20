import json
import requests
import random
import datetime
from tokenleader.app1 import db
from tokenleader.app1.authentication.models import  Otp
from flask import jsonify, make_response, current_app
from  tokenleader.app1.kafka import kafka_producer as kp
from tokenleaderclient.rbac.wfc import WorkFuncContext


class Otpmanager():

    '''    
    1. send otp to user
    3.if otp is already present in the request, check otp validity
    
    '''

    def __init__(self, userObj_fm_db):
        self.userObj_fm_db = userObj_fm_db
        self.userdict_fm_db = userObj_fm_db.to_dict()
        self.otpvalidtime = 30
        self.userid_db = self.userdict_fm_db.get('username')
        self.email_db = self.userdict_fm_db.get('email')
        self.OTP_MODE = self.userdict_fm_db.get('otp_mode')            
        self.existing_otp = userObj_fm_db.otp.otp
        self.OTP_Validation_status = False


    def despatch_otp(self):
        try:
            rand = str(random.random())
            num = rand[-4:]
            if self._save_otp_in_db(num) == True:
                org = self.userdict_fm_db.get('wfc').get('org')
                if org in current_app.config['otp']:
                    otpvalidtime = current_app.config.get('otp').get('org')
                mail_to = self.userdict_fm_db.get('email')
                sms_to = self.userdict_fm_db.get('mobile_num')
                kafka_response = {'status': True, "otp": num,
                                  "otp_sending_method": self.OTP_MODE,
                                  "mail_to": mail_to, "sms_to": sms_to,
                                  'message': ("OTP: %s with validity: %s" 
                                              %(str(num), otpvalidtime)),}
                print(kafka_response)
                conf = {"kafka_servers": current_app.config.get("kafka_servers")}
                kp.notify_kafka(conf, self._get_wfc(), 
                                "topic_tokenleader", kafka_response)
        except Exception as e:
            print(e)
            kafka_response = e
        return kafka_response


    def validate_otp(self, otp_input):
        creation_date = self.userObj_fm_db.otp.creation_date
        org_fm_db = self.userdict_fm_db.get('wfc').get('org')
        if org_fm_db in current_app.config['otp']:
            self.otpvalidtime = current_app.config.get('otp').get('org')
        elapsed_time = (datetime.datetime.utcnow()-creation_date).total_seconds()/60.0
        if elapsed_time <= self.otpvalidtime:
            self.OTP_Validation_status = True
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
                record = Otp(otp=num,userid=self.userid_db,delivery_method=self.OTP_MODE)
    #            print(record)
                db.session.add(record)
                db.session.commit()
            status = True
        except Exception as e:
            record  = e
            print (e)
            status = True
        return status


