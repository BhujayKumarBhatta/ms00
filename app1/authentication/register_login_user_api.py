from flask import request, Blueprint, jsonify,json, current_app,make_response
from app1.authentication.models import User
from app1 import db
import requests

fapp = Blueprint('fapp', __name__)

user = ''
pwd = ''

@fapp.route('/register_user', methods=['POST'])
def register_user():
        try:
            request.get_json(force=True)
            user = str(request.json['username'])
            pwd = str(request.json['password'])
            u1 = User(username=str(user), email=str(request.json['emailid']), role=str(request.json['role']))
            db.session.add(u1)
            db.session.commit()
            u1 = User.query.filter_by(username=str(user)).first()
            u1.set_password(str(pwd))
            db.session.commit()
            if u1:
                 return jsonify({'MSG' : 'Registration Successful'})
            else:
                 return jsonify({'MSG' : 'Registration Unsuccessful'})
        except Exception as e:
            return ('Error:' + str(e))

'''
@fapp.route('/login_user')
def login_user():
        try:
            request.get_json(force=True)
            user = str(request.json['username'])
            pwd = str(request.json['password'])
            print(User.query.all())
            u = User.query.filter_by(username=str(user)).first()
            if u:
                #print(u.to_dict())
                if u.check_password(pwd):
                    return jsonify({'MSG' : 'Login Successful'})
                else:
                    return jsonify({'MSG' : 'Login Unsuccessful'})
            else:
                return jsonify({'MSG' : 'User is not registered yet.'})
        except Exception as e:
            return ('Error:' + str(e))

'''


@fapp.route('/login_user')
def login_and_find_role():
    try:
        request.get_json(force=True)
        user = str(request.json['username'])
        pwd = str(request.json['password'])
        #print(user)
        #print(pwd)
        URL = 'http://127.0.0.1:9898/token/gettoken'
        PARAMS = {"username": user, "password": pwd}
        #print(PARAMS, type(PARAMS))
        r = requests.post(url = URL, data=json.dumps(PARAMS, sort_keys=False)).json()
        #print(r)
        if r["status"] == "success":
            URL = 'http://127.0.0.1:9898/token/verify_token'
            PARAMS = {"auth_token": r["auth_token"]}
            r1 = requests.post(url = URL, data = json.dumps(PARAMS, sort_keys=False)).json()
            role = r1["payload"]["sub"]["role"]
            #print(role)
            return role + '\n'
        else:
            return jsonify({'MSG' : 'Login Unsuccessful'})
    except Exception as e:
        return ('Error:' + str(e))
