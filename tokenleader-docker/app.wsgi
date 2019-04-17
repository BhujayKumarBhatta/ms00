#activate_this = '/mnt/c/mydev/microservice-tsp-billing/tokenleader/venv/bin/activate_this.py'
#with open(activate_this) as file_:
#    exec(file_.read(), dict(__file__=activate_this))

import sys
sys.path.insert(0, '/usr/local/lib/python3.5/site-packages/tokenleader/')

from tokenleader.app  import app as application
