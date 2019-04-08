# from app1 import flask_app_var

from tokenleader import app1
from tokenleader.app1.configs import configs 

from tokenleader.app1.authentication.token_after_login import token_login_bp
from tokenleader.app1.adminops.adminops_restapi import adminops_bp
from tokenleader.app1.catalog.catalog_restapi import catalog_bp
from tokenleader.app1.catalog import models_catalog 


#bp_list = [token_login_bp, catalog_bp]
bp_list = [token_login_bp, adminops_bp, catalog_bp ]

app = app1.create_app(config_map_list= configs.prod_configs_from_file,
                      blue_print_list=bp_list, )

host = configs.flask_default_setiings_map.get('host_name')
port = configs.flask_default_setiings_map.get('host_port')
ssl = configs.flask_default_setiings_map.get('ssl')
ssl_settings = configs.flask_default_setiings_map.get('ssl_settings')



# from tokenleader.app1.adminops.admin_cli_parser import main

def main():   
    if  ssl == 'enabled':
        app.run(ssl_context=ssl_settings, host = host, port=port, )
    else:
        app.run(host = host, port=port, )
    
