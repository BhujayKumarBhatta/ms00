import os
import sys
from urllib.parse import quote_plus
from tokenleader.app1.configs.config_handler import Configs

_HERE = os.path.dirname(__file__)
_SETTINGS_FILE = os.path.join(_HERE, 'tokenleader/tests/test_configs.yml')

must_have_keys_in_yml = {'flask_default',
                         'db',
                         'token',
                         'secrets'
                         }
conf = Configs('tokenleader', _SETTINGS_FILE, must_have_keys_in_yml=must_have_keys_in_yml)

ymldict = conf.yml

dbs = ymldict.get('db').get('database')
raw_connection_string = 'mysql+pymysql://{0}:{1}@{2}:{3}/{4}'.format(dbs.get('UID'), conf.decrypt_password(dbs.get('db_pwd_key_map')), dbs.get('Server'), dbs.get('Port'), dbs.get('Database'))
#converted_safe_uri #use quote_plus to construct the uri
connection_string = quote_plus(raw_connection_string)
 
test_db_conf = { 'SQLALCHEMY_DATABASE_URI': raw_connection_string, 'SQLALCHEMY_TRACK_MODIFICATIONS': False }
# pick up values from yml and construct other confs here
test_conf_list = [test_db_conf ,   ymldict ]