import os
import sys
import argparse

possible_topdir = os.path.normpath(os.path.join(os.path.abspath(sys.argv[0]),
                                                os.pardir,
                                                os.pardir))
apppath = (os.path.join(possible_topdir,
                               'tokenleader',
                               'tokenleader'))

sys.path.insert(0, apppath)
from tokenleader.app1.configs.config_handler import Configs

must_have_keys_in_yml = {'flask_default',
                         'database',
                         'ldap',
                         'testotpmailservice',
                         'otpvalidfortsp',
                         'token',
                         'secrets'
                         }

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
except Exception as e:
    #print usage help when no argument is provided
    parser.print_help(sys.stderr)
    sys.exit(1)
    
def main():
    conf = Configs('tokenleader', must_have_keys_in_yml=must_have_keys_in_yml)
    conf.generate_secret_file(options.keymap, options.password)
