from subprocess import check_output, check_call
try:
        a=check_output(["sudo", "curl", "-i", "-H", "Content-Type: application/json", "-X", "POST", "-d", '{"username":"admin4","emailid":"admin4@itc.in","role":"admin","password":"welcome@1"}' "http://localhost:9999/register_user"])
        print(a)
        if "Registration Successful" in a:
             print('ok')
             b = check_output(["sudo", "curl", "-i", "-H", "Content-Type: application/json", "-X", "GET", "-d", '{"username":"admin4","password":"welcome@1"}', "http://localhost:9999/login_user"]
             print(b)
             if 'admin' in b:
                    print('Admin User')
             else:
                    print('Non-admin User')
except Exception as e:
    print (e)
