# pyconsole
pyconsole is a python library leveraging pexpect to provide simplified interface to access multi-vendor network devices. 

<b> __under development__ </b>

<b> Requirement </b>
<li> python 2.7+ <br>
<li> pexpect 3.0+, tested with 3.3
 
<b> Example </b>
<pre>
rtr1 = PyConsole(connection='telnet 10.18.20.103', 
 os='brocade', user='att', password='att', enable_password='att',)
rtr2 = PyConsole(connection='telnet 10.18.20.104', 
 os='brocade', user='att', password='att', enable_password='att',)
pc1 = PyConsole(connection='ssh -l super 10.17.138.102', 
 os='linux', user='root', password='PassWord')

rtr1.run_commands("""
config term
int eth 1/1
ip address 10.1.1.2/24
enable
end
""" 
</pre>
