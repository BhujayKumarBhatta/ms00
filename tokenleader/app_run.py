# from app1 import flask_app_var

from tokenleader import app1
from tokenleader.app1.configs.config_handler import Configs 


from tokenleader.app1.authentication.token_after_login import token_login_bp
from tokenleader.app1.adminops.adminops_restapi import adminops_bp
# from app1.catalog.catalog_functions import catalog_bp
from tokenleader.app1.catalog import models_catalog 

must_have_keys_in_yml = {'flask_default',
                         'db',
                         'token',
                         'secrets'
                         }

#must_have_in_flask_default_section = {'host_name',
#                             'host_port',
#                             'ssl',
#                             'ssl_settings'
#                             }

conf = Configs('tokenleader', must_have_keys_in_yml=must_have_keys_in_yml)

c = conf.yml

conf_obj = {"conf": conf}
config_list = [conf_obj, c]

#bp_list = [token_login_bp, catalog_bp]
bp_list = [token_login_bp, adminops_bp]

app = app1.create_app(config_map_list= config_list,
                      blue_print_list=bp_list, )

host = c.get('flask_default').get('host_name')
port = c.get('flask_default').get('host_port')
ssl = c.get('flask_default').get('ssl')
ssl_settings = c.('flask_default').get('ssl_settings')



# from tokenleader.app1.adminops.admin_cli_parser import main

def main():   
    if  ssl == 'enabled':
        app.run(ssl_context=ssl_settings, host = host, port=port, )
    else:
        app.run(host = host, port=port, )
    
