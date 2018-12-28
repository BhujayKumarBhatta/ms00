from flask import request, Blueprint, jsonify, current_app,make_response
from app1.authentication.models import User
from app1 import db

fapp = Blueprint('fapp', __name__)

@fapp.route('/register_user', methods=['POST'])
def register_user():
        try:
            request.get_json(force=True)
            u1 = User(username=str(request.json['username']), email=str(request.json['emailid']))
            db.session.add(u1)
            db.session.commit()
            u1 = User.query.filter_by(username=str(request.json['username'])).first()
            u1.set_password(str(request.json['password']))
            db.session.commit()
            if u1:
                 return jsonify({'MSG' : 'Registration Successful'})
            else:
                 return jsonify({'MSG' : 'Registration Unsuccessful'})
        except Exception as e:
            return ('Error:' + str(e))

@fapp.route('/login_user', methods=['GET'])
def login_user():
        try:
            request.get_json(force=True)
            username = str(request.json['username'])
            password = str(request.json['password'])
            print(User.query.all())
            user = User.query.filter_by(username=username).first()
            if user.check_password(password):
                return jsonify({'MSG' : 'Login Successful', 'email' : user.to_dict()['email']})
            else:
                return jsonify({'MSG' : 'Login Unsuccessful'})
        except Exception as e:
            return ('Error:' + str(e))