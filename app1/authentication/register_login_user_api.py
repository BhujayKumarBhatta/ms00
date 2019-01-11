from functools import wraps
from flask import request, render_template, Blueprint, flash, session, jsonify, json, redirect, url_for
from app1.authentication.models import User
from app1 import db
from app1.authentication.login_client import LClient
import requests

fapp = Blueprint('fapp',__name__)

user = ''
pwd = ''

@fapp.route('/register_user', methods=['POST'])
@login_required
@admin_required
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
                    return redirect(url_for('login_user'))
                else:
                    flash("Something went wrong. Register again.")
                    return redirect(url_for('register_user'))
        except Exception as e:
            return ('Error:' + str(e))



def login_required(f):
     @wraps(f)
     def wrap(*args, **kwargs):
         if 'logged_in' in session:
             return f(*args, **kwargs)
         else:
             flash("You need to login first.")
             return redirect(url_for('login_user'))
     return wrap

def admin_required(f):
     @wraps(f)
     def wrap(*args, **kwargs):
         if 'username' in session:
             return f(*args, **kwargs)
         else:
             return redirect(url_for('check_if_admin', username = session['username']))
     return wrap


@fapp.route('/check_if_admin/<username>')
def check_if_admin(username):
     LClient.if_admin(username)

@fapp.route('/login_user')
def login_user():
    try:
        request.get_json(force=True)
        user = str(request.json['username'])
        pwd = str(request.json['password'])
        ses = LClient(user, pwd).login()
        if ses['SESSION']:
           session['logged_in'] = True
           session['username'] = ses['LOGGED_IN_USER']
           return redirect(url_for('dashboard'))
        else:
           flash("Login Unsuccessful")
           return redirect(url_for('login_user'))
    except Exception as e:
        return ('Error:' + str(e))

@fapp.route('/dashboard')
@login_required
def dashboard():
    try:
        return render_template('index.html')
    except Exception as e:
        return ('Error:' + str(e))

@fapp.route('/logout')
@login_required
def logout():
    session.clear()
    flash("You have been logged out!")
    return redirect(url_for('dashboard'))
