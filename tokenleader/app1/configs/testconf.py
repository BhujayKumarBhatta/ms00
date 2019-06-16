import os
import sys
from urllib.parse import quote_plus
from tokenleader.app1.configs.config_handler import Configs
# test_data_path = os.path.join(os.path.dirname(__file__),
#                                os.pardir, 'tests', 'testdata')

_HERE = os.path.dirname(__file__)
TEST_DATA_PATH = os.path.join(_HERE, os.pardir, os.pardir, 'tests' , 'testdata')
SERVER_SETTINGS_FILE = os.path.join(TEST_DATA_PATH, 'test_tokenleader_configs.yml')

CLIENT_CONF_FILE = os.path.join(TEST_DATA_PATH, 'test_client_configs.yml')
must_have_keys_in_yml = {'flask_default',
                         'db',
                         'token',
                         'secrets'
                         }
must_have_in_flask_default_section = {'host_name',
                             'host_port',
                             'ssl',
                             'ssl_settings'
                             }

must_have_in_token_section = {'private_key_file_location',
                              'public_key_file_location',
                             }

must_have_in_db_section = {'database'}

try:
    conf = Configs('tokenleader', SERVER_SETTINGS_FILE, must_have_keys_in_yml=must_have_keys_in_yml)
    ymldict = conf.yml
    flask_default_setiings_map = ymldict.get('flask_default')
    token_settings_map = ymldict.get('token')
    db_settings_map = ymldict.get('db')
    dbs = db_settings_map.get('database')
except:   
    print("did you configured the file {} correctly ? \n"
          "see readme for a sample settings \n".format(conf.config_file))
    sys.exit()

if not flask_default_setiings_map.keys() >= must_have_in_flask_default_section:
    print("{} must have  the following parameters {}  under the flask_default section".format(
       conf.config_file, must_have_in_flask_default_section ))
    sys.exit()
    
    
if not token_settings_map.keys() >= must_have_in_token_section:
    print("{} must have  the following parameters {}  under the flask_default section".format(
       conf.config_file, must_have_in_token_section ))
    sys.exit()
    
    
if not db_settings_map.keys() >= must_have_in_db_section:
    print("{} must have  the following parameters {}  under the flask_default section".format(
       conf.config_file, db_settings_map ))
    sys.exit()


if token_settings_map.get('private_key_file_location') == 'default':
    private_key_filename = os.path.expanduser('~/.ssh/id_rsa')
else:
    private_key_filename = token_settings_map.get('private_key_file_location')
    
if token_settings_map.get('public_key_file_location') == 'default':
    public_key_filename = os.path.expanduser('~/.ssh/id_rsa.pub')
else:
    public_key_filename = token_settings_map.get('public_key_file_location')

with open(private_key_filename, 'r') as f:
        private_key = f.read()
with open(public_key_filename, 'r') as f:
        public_key = f.read()      
key_attr = {'private_key': private_key, 'public_key': public_key}
token_settings_map.update(key_attr)

connection_string = 'mysql+pymysql://{0}:{1}@{2}:{3}/{4}'.format(quote_plus(dbs.get('UID')), quote_plus(conf.decrypt_password(dbs.get('db_pwd_key_map'))), dbs.get('Server'), dbs.get('Port'), dbs.get('Database'))
#converted_safe_uri #use quote_plus to construct the uri
test_db_conf = { 'SQLALCHEMY_DATABASE_URI': connection_string, 'SQLALCHEMY_TRACK_MODIFICATIONS': False }
# pick up values from yml and construct other confs here
test_configs_from_file = {**flask_default_setiings_map, **token_settings_map, **test_db_conf}
test_conf_list = [test_configs_from_file ,   ymldict ]