from subprocess import check_output, check_call
try:
        a=check_output(["sudo", "curl", "-i", "-H", "Content-Type: application/json", "-X", "POST", "-d", '{"username":"admin3","emailid":"admin3@itc.in","role":"admin","password":"welcome@1"}', "http://localhost:9999/register_user"])
        print(a)
        if 'Registration Successful' in str(a):
             print('ok')
             b = check_output(["sudo", "curl", "-i", "-H", "Content-Type: application/json", "-X", "GET", "-d", '{"username":"admin3","password":"welcome@1"}', "http://localhost:9999/login_user"])
             print(b)
             if 'admin' in str(b):
                    print('Admin User')
             else:
                    print('Non-admin User')
except Exception as e:
    print (e)
