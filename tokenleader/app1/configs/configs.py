import os
import sys
import argparse
import konfig

possible_topdir = os.path.normpath(os.path.join(os.path.abspath(sys.argv[0]),
                                                os.pardir,
                                                os.pardir))
apppath = (os.path.join(possible_topdir,
                               'tokenleader',
                               'tokenleader'))

sys.path.insert(0, apppath)

from tokenleader.app1.configs.config_handler import Configs
#con = Configs('tokenleader')
must_have_keys_in_yml = {'flask_default',
                         'db',
                         'token'
                         }

must_have_in_flask_default_section = {'host_name',
                             'host_port',
                             'ssl',
                             'ssl_settings'
                             }

must_have_in_token_section = {'private_key_file_location',
                              'public_key_file_location',
                              'secrets'}

must_have_in_db_section = {'database'}


try:
    conf = Configs('tokenleader', must_have_keys_in_yml=must_have_keys_in_yml)
    c = conf.yml
    flask_default_setiings_map = c.get('flask_default')
    token_settings_map = c.get('token')
    db_settings_map = c.get('db')
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


prod_configs_from_file = [flask_default_setiings_map,
                        token_settings_map,
                        db_settings_map, ]


#test_db_settings_map = {'DEBUG': True,
#                'SQLALCHEMY_DATABASE_URI': 'mysql+pymysql://root:welcome123@tldbserver100:3306/auth',
#                'SQLALCHEMY_TRACK_MODIFICATIONS': False}


#test_configs = [token_settings_map,
#            test_db_settings_map]


parser = argparse.ArgumentParser()

parser.add_argument('-k', '--keymap', 
                  action = "store", dest = "keymap",
                  required = True,
                  help = ("a text name of key against which the encrypted password  will be mapped in yml, ensure the \n"
                          "key name is same as what has been stored  in service_configs.yml , secret section."),
                  default = "")


parser.add_argument('-p', '--password', 
                  action = "store", dest = "password",
                  required = True,
                  help = "tokenleader user password, note down this password , this will be stored as encrypted",
                  default = "")

try:                  
    options = parser.parse_args()    
except:
    #print usage help when no argument is provided
    parser.print_help(sys.stderr)
    sys.exit(1)
    
def main():
    conf.generate_secret_file(options.keymap, options.password)
    
