#!/usr/bin/env python

import re
import sys
from pyconsole import *

user, pswd, enable = 'admin', "password", "password"

# single line cmd
cmdA = 'show ver'

#
# multi line cmd with 
# 1) prompt change (config mode in this case)
# 2) comments ! 
# 3) empty line
cmdB = """
! configure eth1/8 with ip and enable
config term
int eth 1/8
ip address 192.168.1.1/24
enable
end
"""

# single line cmd with pipe line
cmdC = 'show int brief wide | inc Up'


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

def main():
    global cmdA, cmdB, cmdC
    global bcmd1, bcmd2, bcmd3

    # Brocade NetIron 5.6d
    ssh = 'ssh -l admin 10.18.16.54'
    telnet = 'telnet 10.18.16.54'
    console = 'telnet 10.31.184.1 3005'
    
    for subj, sess in zip( 
        ['Test brocade NetIron via ssh.......', 
         'Test brocade NetIron via telnet....', 
         'Test brocade NetIron via console...',
        ], 
        [ssh, telnet, console,],):

        print pyc_msgpanel('', subj)

        test_session(connection=sess, password=pswd, user=user,
            enable_password=enable)

if __name__ == '__main__':
    main()
