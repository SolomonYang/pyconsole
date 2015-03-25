# pyconsole
pyconsole is a python library leveraging pexpect to provide simplified interface to access multi-vendor network devices. 

<b> __under development__ </b>

<b> Requirement </b>
<li> python 2.7+ <br>
<li> pexpect 3.0+, tested with 3.3

 
<b> Example </b>
<pre>
rtr1 = PyConsole(connection='telnet 10.1.1.1', 
 os='brocade', user='user', password='lab', enable_password='lab',)
rtr2 = PyConsole(connection='telnet 10.1.1.2', 
 os='brocade', user='user', password='lab', enable_password='lab',)
pc1 = PyConsole(connection='ssh -l super 10.2.1.1', 
 os='linux', user='root', password='PassWord')

rtr1.run_commands("""config term
int eth 1/1
ip address 10.1.1.2/24
enable
end""" 

output = rtr1.run_commands("show int brief | inc Up")

for line in output.split('\n'):
 if re.search('1/1 .*Up', line):
  print "etherne 1/1 is up"
</pre>
