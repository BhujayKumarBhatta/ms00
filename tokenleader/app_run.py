from tokenleader import app1
#from tokenleader.app1.configs import configs 

from tokenleader.app1.authentication.auth_routes import token_login_bp
from tokenleader.app1.adminops.adminops_restapi import adminops_bp
# from app1.catalog.catalog_functions import catalog_bp
from tokenleader.app1.catalog import models_catalog 
from tokenleader.app1.configs import prodconfigs
# from prodcon import the prod_conf_ist  and  pass it here , 
#conf_obj = {"conf": conf}
#config_list = [conf_obj, c]
#bp_list = [token_login_bp, catalog_bp]
bp_list = [token_login_bp, adminops_bp]
#print(prodconfigs.prod_conf_list)
app = app1.create_app(config_map_list= prodconfigs.prod_conf_list,
                      blue_print_list=bp_list, )
conf=prodconfigs.conf.yml
host = conf.get('flask_default').get('host_name')
port = conf.get('flask_default').get('host_port')
ssl = conf.get('flask_default').get('ssl')
ssl_settings = conf.get('flask_default').get('ssl_settings')



# from tokenleader.app1.adminops.admin_cli_parser import main

def main():   
    if  ssl == 'enabled':
        app.run(ssl_context=ssl_settings, host = host, port=port, )
    else:
        app.run(host = host, port=port, )
    
