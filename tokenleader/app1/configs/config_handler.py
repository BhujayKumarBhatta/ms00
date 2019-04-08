import yaml
import os
import sys
import six
from cryptography.fernet import Fernet



class Configs():
        
    def __init__(self, service_name, conf_file=None, must_have_keys_in_yml={} ):
        #    
        self.must_have_keys_in_yml = must_have_keys_in_yml 
        
        if conf_file:
            self.config_file = conf_file
        else:            
            self.config_file='/etc/tokenleader/{}_configs.yml'.format(service_name)

        if not os.path.exists(self.config_file):
            print("no configuration file found. you need to create a config file "
                  "first in {} ".format(self.config_file))
            sys.exit()
        else:            
            self.yml = self.parse_yml(self.config_file)
#         print(self.general_config.keys()) 
            if  sorted(self.yml.keys()) >= sorted(self.must_have_keys_in_yml):
                pass                                    
                
            else:
                print("{} file must have the following sections {}".format(
                    self.config_file, self.must_have_keys_in_yml ))
                sys.exit()
                    
                    
    def parse_yml(self, file):
        with open(file, 'r') as f:
            try:
                parsed = yaml.safe_load(f)
            except yaml.YAMLError as e:            
                raise ValueError(six.text_type(e))
            return parsed or {}
    
    def  get_fernet_cipher_from_keyfile(self, keyfilepath):
        filepath =  os.path.expanduser(keyfilepath)
        dirpath = os.path.dirname(filepath)
        if not os.path.exists(dirpath):
            os.makedirs(dirpath)        
        if not  os.path.exists(keyfilepath):
            key = Fernet.generate_key()
            with open(filepath, 'wb') as f:
                f.write(key)
        
        with open(filepath, 'rb') as f:
           file_content = f.readline()        
           cipher_suite = Fernet(file_content)        
           return cipher_suite
        
    
    def generate_secret_file(self, key_map, text_pwd):
        '''
        stores encrypted password. user should use a cli utility to call this method to generate 
        the file
        '''
        file_loc_from_yml = self.yml.get('secrets').get('secrets_file_location')
        print(file_loc_from_yml)
        filepath =  os.path.expanduser(file_loc_from_yml)
        dirpath = os.path.dirname(filepath)
        if not os.path.exists(dirpath):
            os.makedirs(dirpath)  
                      
        if  os.path.exists(filepath): 
            existing_secrets = self.parse_yml(filepath)
                        
        else:
            existing_secrets = {}
            
        cipher_suite = self.get_fernet_cipher_from_keyfile(
            self.yml.get('secrets').get('fernet_key_location'))
        
        byte_password = text_pwd.encode("utf-8")
        encrypted_password = cipher_suite.encrypt(byte_password)
        encrypted_password_text = bytes(encrypted_password).decode("utf-8")                 
              
        new_secrets = {key_map: encrypted_password_text}
        existing_secrets.update(new_secrets) 
        
        with open(filepath, 'w') as f:
            yaml.dump(existing_secrets, f, default_flow_style=False)
            msg =  ("file {} has been generated".format(filepath))
        
        print(msg)
        return self
        

    def decrypt_password(self, key_map):                
       
        file_loc_from_yml = self.yml.get('secrets').get('secrets_file_location')
        filepath =  os.path.expanduser(file_loc_from_yml)
        
        try:    
            cipher_suite = self.get_fernet_cipher_from_keyfile(
            self.yml.get('secrets').get('fernet_key_location'))
                    
            secret_yml = self.parse_yml(filepath)
            encrpted_text_from_file = secret_yml.get(key_map)               
            msg = "got the encrypted the password"
            
            byte_encrpted_text = encrpted_text_from_file.encode("utf-8")            
            byte_decrpted_text = cipher_suite.decrypt(byte_encrpted_text)
            clear_decrypted_text = bytes(byte_decrpted_text).decode("utf-8")  
            
        except Exception as e:
            msg = " secret  file or the keymap or fernetkey file is not found, the full error is {}".format(e)
            print(msg)
            clear_decrypted_text = ""            
            sys.exit()     
            
        return clear_decrypted_text   
    
    

#     
