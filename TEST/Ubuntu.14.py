#!/usr/bin/env python


import re
import sys
from pyconsole import *

cmdA, cmdB, cmdC = None, None, None
user, pswd, enable = 'test', "test", "test"

cmdA = 'uname -a'

cmdB = """
ls
ps
"""

# single line cmd with pipe line
cmdC = 'ps -ef | grep python'

def test_session(**kwargs):
    global cmdA, cmdB, cmdC

    sess = PyConsole(**kwargs)

    if not sess.active:
        print 'Error to initialize session....'
        return -1

    # single cmd
    output = sess.run_commands(cmdA)
    print '\n\n'
    print pyc_msgpanel('', 'Output of Command A - single cmd')
    print pyc_line_by_line(output)

    # multiple cmds + change prompts -> rtr(config)#
    output = sess.run_commands(cmdB)
    print '\n\n'
    print pyc_msgpanel('', 'Output of Command B - multiple cmd')
    print pyc_line_by_line(output)

    # single cmd with pipeline
    output = sess.run_commands(cmdC)
    print '\n\n'
    print pyc_msgpanel('', 'Output of Command C - single cmd with pipeline')
    print pyc_line_by_line(output)


def test_linux(): 
    test_session(connection='ssh -l super 10.17.138.102', 
                 os='linux', device_type='pc', 
                 user='super', password='Br0cade1')

if __name__ == '__main__':
    test_linux()
