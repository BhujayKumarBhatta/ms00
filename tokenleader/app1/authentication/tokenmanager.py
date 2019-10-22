import jwt
import datetime
from tokenleader.app1.catalog.models_catalog import ServiceCatalog
from flask import  current_app




class TokenManager():
    '''
    '''
    def __init__(self, user_dict_fm_db):
        self.user_dict_fm_db = user_dict_fm_db
        self.tokenexpiration=30
        self.privkey=None
#         print(current_app.config.get('token').get('tokenexpiration'))
        if 'tokenexpiration' in current_app.config.get('token'):
            self.tokenexpiration = current_app.config.get('token').get('tokenexpiration')
        self.privkey = current_app.config.get('private_key')


    def get_token(self):
        print(self.user_dict_fm_db)
        exp = datetime.datetime.utcnow() + datetime.timedelta(days=0, seconds=self.tokenexpiration)
        payload = { 'exp': exp,
                    'iat': datetime.datetime.utcnow(),
                    'sub': self.user_dict_fm_db  }
        auth_token = self.generate_encrypted_auth_token(payload, self.privkey)

        response = {'status': 'success',
                    'message': 'success',
                    'auth_token': auth_token.decode(),
                    'service_catalog': self._service_catalog()}
        return response


    def _service_catalog(self):
        svcs = ServiceCatalog.query.all()
        service_catalog = {}
        for s in svcs:
            service_catalog[s.name]=s.to_dict()
        return service_catalog



    def generate_encrypted_auth_token(self, payload, priv_key):
#         print(payload)
#         print(priv_key)
        try:
            auth_token = jwt.encode(
                 payload,
                 priv_key,
                 algorithm='RS512'
            )
            return auth_token
        except Exception as e:
            return e


    def decrypt_n_verify_token(self, auth_token, pub_key):
#         print(pub_key)
        try:
            payload = jwt.decode(
                auth_token,
                pub_key,
                algorithm=['RS512']
            )

            return payload
        except jwt.ExpiredSignatureError:
            return 'Signature expired. Please log in again.'
        except jwt.InvalidTokenError:
            return 'Invalid token. Please log in again.'




