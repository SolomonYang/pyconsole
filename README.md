# pyconsole
pyconsole is a python library leveraging pexpect to provide simplified interface to access multi-vendor network devices. 

<b> __under development__ </b>

<b> Requirement </b>
<li> python 2.7+ <br>
<li> pexpect 3.0+, tested with 3.3

<b> Tested</b>
<pre>
  Vendor  OS       Version    Methods
- Cisco   IOS      12.2SE     telnet/ssh/console
- Brocade NetIron  5.6b       telnet/ssh/console
- Brocade FastIron 7.2h       telnet/ssh/console
- Ubuntu  Ubuntu   14.0       ssh

Please see the logs under TEST directory
</pre>
 
<b> Example </b>
<pre>
#!/usr/bin/env python


import re
import sys
from pyconsole import *

# Brocade NetIron 5.6
rtr1 = PyConsole(connection='ssh -l admin 192.168.1.54',
                 password='password', enable_password='password')

# Cisco IOS 12.2
rtr2 = PyConsole(connection='telnet 192.168.1.23',
                 user='admin', password='password', enable_password='password')

# Linux Ubuntu 14.0
linux1 = PyConsole(connection='ssh -l super 192.168.1.102',
                os='linux', password='PassWord')

rtr1.run_commands("""
config term
int eth 1/1
ip address 10.1.1.2/24
enable
end
""")

output1 = rtr2.run_commands("show int brief | inc Up")

output2 = linux1.run_commands("ps -ef | grep python")

for line in output1.split('\n'): 
    if re.search('1/1 .*Up', line): 
        print "etherne 1/1 is up"

</pre>
