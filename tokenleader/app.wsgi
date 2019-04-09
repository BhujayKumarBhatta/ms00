import os
import sys

activate_this = '/opt/tokenleader/venv/bin/activate_this.py'
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

sys.path.insert(0, '/opt/tokenleader/')

from tokenleader.app_run  import app as application



