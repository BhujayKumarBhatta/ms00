import requests
import json
from app1.authentication.models import User
#from flask import jsonify

class LClient(object):
    def __init__(self, uname, pwd):
        self.uname = uname
        self.pwd = pwd

    def login(self):
        try:
            URL = 'http://127.0.0.1:9898/token/gettoken'
            PARAMS = {"username": uname, "password": pwd}
            r = requests.post(url = URL, data=json.dumps(PARAMS, sort_keys=False)).json()

            if r["status"] == "success":
                URL = 'http://127.0.0.1:9898/token/verify_token'
                PARAMS = {"auth_token": r["auth_token"]}
                r1 = requests.post(url = URL, data = json.dumps(PARAMS, sort_keys=False)).json()

                if r1["status"] == 'Verification Successful':
                    return json.dumps({'MSG' : 'Login Successful', 'LOGGED_IN_USER' : r1["payload"]["sub"]["username"], 'SESSION' : 'STORED'}, sort_keys=False)

                else:
                    return json.dumps({'MSG' : 'Unauthorized'}, sort_keys=False)

            else:
                return json.dumps({'MSG' : 'Login Unsuccessful'}, sort_keys=False)

        except Exception as e:
             return e

    def if_admin(uname):
        user = User.query.filter_by(username=uname).first()
        if user.is_admin() == True:
            return json.dumps({'ADMIN' : True}, sort_keys=False)
        else:
            return json.dumps({'ADMIN' : False}, sort_keys=False)
