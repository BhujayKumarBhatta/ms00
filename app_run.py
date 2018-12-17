# from app1 import flask_app_var

import app1
from app1.configs import configs 

from app1.authentication.check_req_obj import req_obj_bp
from app1.authentication.tokenops import token_bp 
from app1.authentication.token_after_login import token_login_bp

bp_list = [req_obj_bp,token_bp,token_login_bp]

app = app1.create_app(config_map_list= configs.prod_configs_from_file,
                      blue_print_list=bp_list)