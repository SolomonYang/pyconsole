#!/usr/bin/env python


import re
import sys
from pyconsole import *

user, pswd, enable = 'test', "test", "test"

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
int g0/28
ip address 192.168.1.1 255.255.255.0
no shut
end
"""

cmdC = 'show ip int brief | inc up'


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
    # Cisco Cisco-IOS-C3560G-24TS, 12.2(58)SE2 
    ssh = 'ssh -l test 10.17.145.23' 
    telnet = 'telnet 10.17.145.23' 
    console = 'telnet 10.31.184.8 3006'

    for subj, sess in zip( 
        ['Test cisco/ios via ssh.......', 
         'Test cisco/ios via telnet....', 
         'Test cisco/ios via console...',
        ], 
        [ssh, telnet, console, ],
        ):

        print pyc_msgpanel('', subj) 
        test_session(connection=sess, password=pswd, user=user, 
            enable_password=enable,
            )


if __name__ == '__main__':
    main()
