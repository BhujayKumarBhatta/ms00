#! venv/bin/python

# -*- coding: utf-8 -*-

import os
import sys
import argparse
import subprocess


possible_topdir = os.path.normpath(os.path.join(os.path.abspath(sys.argv[0]),
                                                os.pardir,
                                                os.pardir))
apppath = (os.path.join(possible_topdir,
                               'tokenleader',
                               'tokenleader'))

sys.path.insert(0, apppath)

migration_dir = apppath+'/migrations'
from tokenleader.app1.adminops.admin_cli_parser import main

if __name__ == '__main__':		
	main()
	
	
	