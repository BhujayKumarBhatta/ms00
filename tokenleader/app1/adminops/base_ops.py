from tokenleader.app1.authentication.models import Organization, OrgUnit, Department, Workfunctioncontext, Role, User
from tokenleader.app1 import db
from sqlalchemy import exc

def get_input(text):
    return input(text)

def get_validated_roles(roles):
    '''
    param roles: comma separeted text for role name within  a list
    type: list
    
    '''
    valid_role_list =[]
    invalid_role_list = []
    
    for role in roles:        
        r = Role.query.filter_by(rolename=role).first()        
        if r:
            valid_role_list.append(r)            
        else:            
    
            invalid_role_list.append(role)
    if  invalid_role_list:        
        msg = ("following roles: {} does not exist, create it first".format(invalid_role_list))
        print(msg)    
    if valid_role_list:
        return valid_role_list

def register_ops1(obj, cname, orgname=None, ou_name=None, dept_name=None, wfc_name=None, roles=None,
                   email=None, pwd=None, **kwargs):    
    record = None    
    if obj == 'Organization' :        
        otype = 'inernal'
        org_auth_backend = 'standard'
        if 'orgtype' in kwargs:
            otype = kwargs['orgtype']   
        if 'auth_backend' in kwargs:
            org_auth_backend = kwargs['auth_backend'] 
        record =  Organization(name=cname, orgtype=otype, auth_backend=org_auth_backend)  
    if obj == 'OrgUnit' :
        record =  OrgUnit(name=cname)
    if obj == 'Department' :
        record =  Department(name=cname)
    if obj == 'Role' :
        record = Role(rolename=cname)
    if obj == 'Workfunctioncontext' :
        try:
            o = Organization.query.filter_by(name=orgname).first()
            ou = OrgUnit.query.filter_by(name=ou_name).first()
            dept = Department.query.filter_by(name=dept_name).first()        
        except Exception as e:
            msg = "Organization, organization Unit or department name not found\
                   register them first in the respective master db, \
                   the error is {}".format(e)
            print(msg)
            return None      
        record =  Workfunctioncontext(name=cname, org=o, orgunit=ou, department=dept ) 
    if obj == 'User':
        if wfc_name:
            try:
                wfc = Workfunctioncontext.query.filter_by(name=wfc_name).first()
            except Exception as e:
                msg = ("wfc  not found in database register them first in the wfc master db"
                       "the error is ")
                print(msg)
                return None   
        if roles:
            valid_role_objects = get_validated_roles(roles)
            if  isinstance(valid_role_objects, list):          
                record = User(username=cname, email=email, roles=valid_role_objects, wfc=wfc)
                record.set_password(pwd)
            else:
                msg = "user registration aborted"  
        else:            
            record = User(username=cname, email=email)
            record.set_password(pwd)   
                   
    if record:
        try:
            db.session.add(record)        
            db.session.commit()
            msg = "{} has been registered.".format(cname)         
        except exc.IntegrityError:
            msg = ('databse integrity error, {} by the same name may be already present'.format(
                cname))
            db.session.rollback()
            #raise
        except  Exception as e:
            msg =("{} could not be registered , the erro is: \n  {}".format(cname, e))
            db.session.rollback() 
    print(msg)
    return msg


def get_records_from_db(obj, cname=None):
    record = None
    record_list = None
    if obj == 'Organization' :
        if cname:
            record = Organization.query.filter_by(name=cname).first()
#             print('got record  {}'.format(record))         
        else:            
            record_list = Organization.query.all()
#             print('got record list {}'.format(record_list))        
    if obj == 'OrgUnit':
        if cname:
            record = OrgUnit.query.filter_by(name=cname).first()        
        else:
            record_list = OrgUnit.query.all()
    if obj == 'Department':
        if cname:
            record = Department.query.filter_by(name=cname).first()        
        else:
            record_list = Department.query.all()   
    if obj == 'Workfunctioncontext':
        if cname:
            record = Workfunctioncontext.query.filter_by(name=cname).first()        
        else:
            record_list = Workfunctioncontext.query.all()
    if obj == 'Role':
        if cname:
            record = Role.query.filter_by(rolename=cname).first()        
        else:
            record_list = Role.query.all()
    if obj == 'User':        
        if cname:
            record = User.query.filter_by(username=cname).first()        
        else:
            #print('i am inside dbops recordlist')
            record_list = User.query.all()  
               
    if record_list:
        return record_list
    else:
        return record
   
        
def delete_ops(obj, cname):
    record = None    
    record = get_records_from_db(obj, cname)   
    if  record: 
    #print('obj is  {}'.format(obj))
        try:
            db.session.delete(record)        
            db.session.commit()
            status = "{} has been  deleted successfully".format(cname) 
            print(status)
            #print('i am here')
            return status
        except  Exception as e:
                status = "{} could not be deleted , the erro is: \n  {}".format(cname, e)
                print(status)
                #return status
    else:
        status = "{}  not found in database".format(record)
        print(status)
    
    return status
    #return "i am return last"   

def list_ops(obj, cname=None, *args, **kwargs):
    record = None
    record_list = []
    
    if cname:
        record = get_records_from_db(obj, cname)
        if obj == 'Role':
            result = {"id": record.id, "name":  record.rolename }
            print(result) 
        elif obj == 'User':
#             print(record.username, record.email, ','.join([r.rolename for r in record.roles]))
            result = record.to_dict()
            print(result)
        else: 
            result = {'id': record.id, 'name': record.name , 'record': record}
            print(result)
             
        return result
    else:
        #print('i am inside list ops')
        record_list = get_records_from_db(obj)
#         print(" i got the record list from db {}".format(record_list))
        record_list_of_dict = []
        for record in record_list:
            if obj == 'Role':
                result = {"id": record.id, "name":  record.rolename }
                print(result) 
            elif obj == 'User':
#                 print("id: {},  name: {}".format(record.id, record.username))
#                 print(record.username, record.email, ','.join([r.rolename for r in record.roles]))
                record_to_dict = (record.to_dict())
#                 print('i got the record  to dict from record list {}'.format(record_to_dict))
                record_list_of_dict.append(record_to_dict)
#                 print('i am on the loop  result {}'.format(record_list_of_dict))
                result = record_list_of_dict
                print(result)
            else:            
                result = {'id': record.id, 'name': record.name , 'record': record}
                print(result)                
#         print('i am on the final result {}'.format(result))        
        return result  
                            
           
#     if record:
        
#     else:
#         print("Not Found  any record by that name, try full lisitng")       
# #     
# #     if record_list:   
        #print('i am inside record list {}'.format(record_list))     
        
   
        
#     else:
#         print("Looks the list is empty , nothing has been registered yet")  

#wfcorg: {}, wfcou: {}, wfcdept: {}

# record.functional_context.org.name,
#                                                            record.functional_context.orgunit.name,
#                                                            record.functional_context.department.name

# print("id: {},  name: {} , wfc: {} , wfcorg: {}, wfcou: {}, wfcdept: {}".format(record.id,
#                                                            record.rolename, 
#                                                            record.functional_context.name,
#                                                            record.functional_context.org.name,
#                                                            record.functional_context.orgunit.name,
#                                                            record.functional_context.department.name
#                                                            ))