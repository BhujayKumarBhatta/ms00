import os
import sys
from urllib.parse import quote_plus
from tokenleader.app1.configs.config_handler import Configs

_HERE = os.path.dirname(__file__)
_SETTINGS_FILE = os.path.join(_HERE, '../../tests/test_configs.yml')

must_have_keys_in_yml = {'flask_default',
                         'database',
                         'ldap',
                         'testotpmailservice',
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

must_have_in_db_section = {'Server',
                           'Port',
                           'Database',
                           'UID',
                           'db_pwd_key_map'
                          }

must_have_in_ldap_default_section = {'Server',
                                     'Port',
                                     'Version'
                                    }

must_have_in_mail_default_section = {'Server',
                                     'Port'
                                    }

try:
    conf = Configs('tokenleader', _SETTINGS_FILE, must_have_keys_in_yml=must_have_keys_in_yml)
    ymldict = conf.yml
    flask_default_setiings_map = ymldict.get('flask_default')
    ldap_default_settings_map = ymldict.get('ldap')
    mailservice_default_settings_map = ymldict.get('testotpmailservice')
    token_settings_map = ymldict.get('token')
    dbs = ymldict.get('database')
except:   
    print("did you configured the file {} correctly ? \n"
          "see readme for a sample settings \n".format(conf.config_file))
    sys.exit()

if not flask_default_setiings_map.keys() >= must_have_in_flask_default_section:
    print("{} must have  the following parameters {}  under the flask_default section".format(
       conf.config_file, must_have_in_flask_default_section ))
    sys.exit()

if not ldap_default_settings_map.keys() >= must_have_in_ldap_default_section:
    print("{} must have  the following parameters {}  under the flask_default section".format(
       conf.config_file, must_have_in_ldap_default_section ))
    sys.exit()

if not mailservice_default_settings_map.keys() >= must_have_in_mail_default_section:
    print("{} must have  the following parameters {}  under the flask_default section".format(
       conf.config_file, must_have_in_mail_default_section ))
    sys.exit()
    
if not token_settings_map.keys() >= must_have_in_token_section:
    print("{} must have  the following parameters {}  under the flask_default section".format(
       conf.config_file, must_have_in_token_section ))
    sys.exit()
    
    
if not dbs.keys() >= must_have_in_db_section:
    print("{} must have  the following parameters {}  under the flask_default section".format(
       conf.config_file, must_have_in_db_section ))
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
ldap_conn_string = 'ldap://{0}:{1}'.format(ldap_default_settings_map.get('Server'),ldap_default_settings_map.get('Port'))
mail_service_for_otp = 'http://{0}:{1}/mail'.format(mailservice_default_settings_map.get('Server'), mailservice_default_settings_map.get('Port'))
#converted_safe_uri #use quote_plus to construct the uri
test_db_conf = { 'SQLALCHEMY_DATABASE_URI': connection_string, 'SQLALCHEMY_TRACK_MODIFICATIONS': False, 'LDAP_PROVIDER_URL': ldap_conn_string, 'LDAP_PROTOCOL_VERSION': ldap_default_settings_map.get('Version'), 'MAIL_SERVICE_URI': mail_service_for_otp}
# pick up values from yml and construct other confs here
test_configs_from_file = {**flask_default_setiings_map, **token_settings_map, **test_db_conf}
test_conf_list = [test_configs_from_file ,   ymldict ]