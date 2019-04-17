import os
from urllib.parse import quote_plus
from tokenleader.app1.configs.config_handler import Configs
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
    conf = Configs('tokenleader', must_have_keys_in_yml=must_have_keys_in_yml)
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

connection_string = 'mysql+pymysql://{0}:{1}@{2}:{3}/{4}'.format(quote_plus(dbs.get('UID')), conf.decrypt_password(dbs.get('db_pwd_key_map')), dbs.get('Server'), dbs.get('Port'), dbs.get('Database'))
#converted_safe_uri #use quote_plus to construct the uri
prod_db_conf = { 'SQLALCHEMY_DATABASE_URI': connection_string, 'SQLALCHEMY_TRACK_MODIFICATIONS': False }
# pick up values from yml and construct other confs here
prod_configs_from_file = {**flask_default_setiings_map, **token_settings_map, **prod_db_conf}
prod_conf_list = [prod_configs_from_file ,   ymldict ]
