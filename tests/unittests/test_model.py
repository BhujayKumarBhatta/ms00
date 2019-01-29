import unittest
from app1 import db
from app1.authentication import models
from app1.authentication.models import User
from tests.base_test import  BaseTestCase
#app.app_context().push()

class TestUserModel(BaseTestCase):
    '''
    (venvp3flask) bhujay@DESKTOP-DTA1VEB:/mnt/c/mydev/myflask$ python -m unittest discover tests
    '''
    
    def test_user_creation(self):
        u1 = User(username='susan', email='susan@abc.com')
        u1.set_password('mysecret')       
        self.assertTrue(u1.check_password('mysecret'))
        db.session.add(u1)        
        db.session.commit()
        u1 = User.query.filter_by(username='susan').first()
        self.assertTrue(u1.check_password('mysecret'))
    

    
    