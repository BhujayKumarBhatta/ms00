import json

class TLException(Exception):
    status = "UNKNOWN_STATUS"
    message = "Unknown status"

    def __init__(self, status=None, message=None):
        if status:  self.status = status
        if message: self.message = message
        self.ret_val = {"status": self.status, "message": self.message}
#         super(MyException, self).__init__({"status": self.status, "message": self.message})

    def __str__(self):
        return json.dumps(self.ret_val)


    def __repr__(self):
        return self.ret_val


class SException(TLException):
    status = "S status"
    message = "S message"

def checkme(a, b):
    if a==b:
        print("OK")
    else:
        raise SException

try:
    checkme(1,2)
except Exception as e:
    print("only e:", e)
    print("repr:", e.__repr__())
    print(type(e))