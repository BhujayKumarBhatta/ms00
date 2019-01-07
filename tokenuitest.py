from subprocess import check_output, check_call
try:
        a=check_output(["sudo", "curl", "-i", "-H", "Content-Type: application/json", "-X", "POST", "-d", '{"username":"admin","emailid":"admin@itc.in","role":"admin","password":"welcome@123"}', "http://localhost:9999/register_user"])
        if 'HTTP/1.1 200 OK' in str(a):
             b = check_output(["sudo", "curl", "-i", "-H", "Content-Type: application/json", "-X", "GET", "-d", '{"username":"admin","password":"welcome@123"}', "http://localhost:9999/login_user"])
             if 'admin' in str(b):
                    print('Admin User')
             else:
                    print('Non-admin User')
except Exception as e:
    print (e)
