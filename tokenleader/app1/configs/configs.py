import os
import sys
import konfig


   

_HERE = os.path.dirname(__file__)
# _SETTINGS_FILE = os.path.join(_HERE, 'settings.ini')

_SETTINGS_FILE = os.path.join(_HERE, '/etc/tokenleader/tokenleader_settings.ini')

must_have_in_flask_default_section = {'host_name',
                              'host_port',
                              'ssl',
                              'ssl_settings'}

must_have_in_token_section = {'private_key_file_location',
                              'public_key_file_location'}

must_have_in_db_section = {'SQLALCHEMY_DATABASE_URI'}


try:
    CONFS = konfig.Config(_SETTINGS_FILE)
    flask_default_setiings_map = CONFS.get_map('flask_default')
    token_settings_map = CONFS.get_map('token')
    db_settings_map = CONFS.get_map('db')
except:   
    print("did you configured the file {} correctly ? \n"
          "see readme for a sample settings \n".format(_SETTINGS_FILE))
    sys.exit()
    
    
if not flask_default_setiings_map.keys() >= must_have_in_flask_default_section:
    print("{} must have  the following parameters {}  under the flask_default section".format(
       _SETTINGS_FILE, must_have_in_flask_default_section ))
    sys.exit()
    
    
if not token_settings_map.keys() >= must_have_in_token_section:
    print("{} must have  the following parameters {}  under the flask_default section".format(
       _SETTINGS_FILE, must_have_in_token_section ))
    sys.exit()
    
    
if not db_settings_map.keys() >= must_have_in_db_section:
    print("{} must have  the following parameters {}  under the flask_default section".format(
       _SETTINGS_FILE, db_settings_map ))
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


prod_configs_from_file = [flask_default_setiings_map,
                        token_settings_map,
                        db_settings_map, ]


test_db_settings_map = {'DEBUG': True,
                'SQLALCHEMY_DATABASE_URI': 'mysql+pymysql://root:welcome123@tldbserver100:3306/auth',
                'SQLALCHEMY_TRACK_MODIFICATIONS': False}


test_configs = [token_settings_map,
            test_db_settings_map]




    
