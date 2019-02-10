# from app1 import flask_app_var

import app1
from app1.configs import configs 


from app1.authentication.token_after_login import token_login_bp
# from app1.catalog.catalog_functions import catalog_bp
from app1.catalog import models_catalog 

#bp_list = [token_login_bp, catalog_bp]
bp_list = [token_login_bp]

app = app1.create_app(config_map_list= configs.prod_configs_from_file,
                      blue_print_list=bp_list)