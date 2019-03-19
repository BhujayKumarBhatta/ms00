# import os
import sys
# from tokenleader.app_run import app   
from tokenleader.app1 import db
from sqlalchemy import exc
from tokenleader.app1.authentication import models
from tokenleader.app1.authentication.models import User, Role, Workfunctioncontext, Organization, OrgUnit, Department
from tokenleader.app1.adminops import base_ops as bops


def register_org(oname):   
   return bops.register_ops1('Organization', oname)


def list_org(oname=None):
    return bops.list_ops('Organization', oname)

    
def delete_org(oname):
   return  bops.delete_ops('Organization', oname)

def register_ou(ouname):
    return bops.register_ops1('OrgUnit', ouname)
   

def list_ou(ouname=None):
    return bops.list_ops('OrgUnit', ouname)

    
def delete_ou(ouname):
   return  bops.delete_ops('OrgUnit', ouname)

def register_dept(deptname):
    return bops.register_ops1('Department', deptname )  


def list_dept(depatname=None):
    return bops.list_ops('Department', depatname)
    
    
def delete_dept(deptname):
   return  bops.delete_ops('Department', deptname)


def register_work_func_context(fname, orgname, ou_name, dept_name):
    return bops.register_ops1('Workfunctioncontext', fname, orgname, ou_name, dept_name )


def list_wfc(wfcname=None):
    return bops.list_ops('Workfunctioncontext', wfcname)    
    
def delete_wfc(wfcname):
   return  bops.delete_ops('Workfunctioncontext', wfcname)
    

def register_role(rname):
    return bops.register_ops1('Role', rname)


def list_role(rolename=None):
    return bops.list_ops('Role', rolename)

def delete_role(rolename):
    return bops.delete_ops('Role', rolename)   

    
def register_user(uname, email, pwd, wfc_name, roles=None ):
    return bops.register_ops1('User', uname, email=email, pwd=pwd, wfc_name=wfc_name, roles=roles, )   
#  

def list_users(uname=None):
    return bops.list_ops('User', uname)
    
def list_services(services=None):
    return bops.list_services('Services', services)
    
def delete_user(uname):
   return bops.delete_ops('User', uname)
    

def get_input(text):
    return input(text)

# 