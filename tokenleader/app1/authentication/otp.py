import json
import requests
import random
import datetime
from tokenleader.app1 import db
from tokenleader.app1.authentication.models import User, Organization, Otp
from flask import jsonify, make_response, current_app
from  tokenleader.app1.kafka import kafka_producer as kp
from tokenleaderclient.rbac.wfc import WorkFuncContext


class Otpmanager():

    '''    
    1. send otp to user
    3.if otp is already present in the request, check otp validity
    
    '''

    def __init__(self, userdict_fm_db):
        self.userdict_fm_db = userdict_fm_db
        self.otpvalidtime = 30
        self.userid_db = userdict_fm_db.get('username')
        self.email_db = userdict_fm_db.get('email')
        self.OTP_MODE = userdict_fm_db.get('otp_mode')


    def despatch_otp(self):
        try:
            rand = str(random.random())
            num = rand[-4:]
            self._save_otp_in_db(num, self.userid_db)
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


    def validate_otp(self):
        pass


    def _get_wfc(self):
        wfc = WorkFuncContext()
        wfc.setcontext(self.userid_db, self.email_db, self.userdict_fm_db)
        return wfc


    def _save_otp_in_db(self,num, userid):
        ''' not storing the old otp records to reuce database load'''
        try:
            user = User.query.filter_by(id=userid).first()        
            found = Otp.query.all()
            if found:
                lastotp = Otp.query.filter_by(is_active='Y').first()
                if lastotp:
                    print('updating the existing otp :%s by newotp: %s'
                          %(lastotp.otp, num))
                    lastotp.otp = num
                    db.session.commit()
                    record = lastotp
            else:
                print('adding a newe otp in otp table')
                record = Otp(otp=num,userid=userid,delivery_method=self.OTP_MODE)
    #            print(record)
                db.session.add(record)
                db.session.commit()
                return True
        except Exception as e:
            record  = e
        return record


