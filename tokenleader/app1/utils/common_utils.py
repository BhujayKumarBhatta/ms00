import yaml
import six
from flask import current_app

def reload_configs(): 
    file = current_app.config.get('SERVER_SETTINGS_FILE')       
    with open(file, 'r') as f:
        try:
            parsed = yaml.safe_load(f)
        except yaml.YAMLError as e:            
            raise ValueError(six.text_type(e))
        return parsed or {}
        