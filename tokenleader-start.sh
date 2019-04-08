#! venv/bin/python

# -*- coding: utf-8 -*-

import os
import sys
import argparse
<<<<<<< HEAD


possible_topdir = os.path.normpath(os.path.join(os.path.abspath(sys.argv[0]),
                                               os.pardir,
                                               os.pardir))
apppath = (os.path.join(possible_topdir,
                               'tokenleaderclient',
                               'tokenleaderclient'))

sys.path.insert(0, apppath)

from tokenleader.app_run import main

if __name__ == '__main__': 
	 main()
	 
=======



possible_topdir = os.path.normpath(os.path.join(os.path.abspath(sys.argv[0]),
                                                os.pardir,
                                                os.pardir))
apppath = (os.path.join(possible_topdir,
                               'tokenleaderclient',
                               'tokenleaderclient'))

sys.path.insert(0, apppath)

from tokenleader.app_run import main

if __name__ == '__main__': 
	 main()
>>>>>>> 212dfebfb383adaf399f0581bb7720c84418ff63
