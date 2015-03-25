'''
Base class for pyconsole
1) Define network devices and store necessary varibles like connection, 
   ip, protocol, port, username, password, enable_password etc.
2) Initialize Telnet/Console/SSH connections to network devices
3) Provide a simplified API interface to user application and hide low-level 
   connection interactions
4) Support multi vendor OS's/devices - Cisco IOS/XR/NxOS, Brocade Netiron, etc
'''

import re
import sys
import time
import pexpect

DEFAULT_USER = ''
DEFAULT_PASSWORD = ''
ENABLE_PASSWORD = ''
MAX_READ = 163840
DEFAULT_SHORT_TIMEOUT = 5

#!----------------------------------------------------------------------------!#
class PyConsole:
	'''
	'''
	def __init__(self, connection, user=DEFAULT_USER, password=DEFAULT_PASSWORD, 
				 enable_password=ENABLE_PASSWORD, hostname='', vendor='', os='', 
				 device='router', version='', verbose=True):

		# internal variables
		self.CRLF = '\r\n'
		self.prompt_line = ''

		self.conn = connection
		self.user = user
		self.password = password
		self.enable_password = enable_password
		self.device = device
		self.vendor = vendor
		self.os = os
		self.version = version
		self.verbose = verbose

		#
		# if no hostname prvoided, the prompt_list would be ['#', '>']
		#
		self.hostname = hostname.strip()
		self.prompt_list = [self.hostname+'#', self.hostname+'>', '\$']

		self.child = None

		self.debug = 0

		if self.connect() == -1:
			print 'Error to start connection to %s' % self.conn
			return 

		self.collect_sysinfo()
		
		self.post_connect()

	def print_debug_message(self, msg, msg_level=9):
		if self.debug >= msg_level:
			print '\n' + msg

	def debug_session_info(self, msg_level=2):
		if self.debug >= msg_level: 
			print self.conn
			print self.child.before 
			print self.child.after

	def sendline(self, cmd): 
		'''
		pexpect.sendline() uses os.linesep after string, which is '\n' in 
		POSIX, which does not work in network device. So use \r\n instead.
		'''

		if self.device == 'router' :
			return self.child.send(cmd.strip() + self.CRLF)
		else:
			return self.child.send(cmd.strip() + '\n')

	def chop_off_buffer(self, cmd):
		'''
		When using pexpect via SSH for some devices like Brocade FSX800/7.4h
		the pexpect.buffer will start with multiple lines of prompts, like
		"\r\n\r\nSSH@HOST#\r\nSSH@HOST#\r\n\r\nSSH@HOST#show version", which
		makes pexpect.expect return prematurely. 

		My solution is to chop off the unnecessary prompt lines from 
		pexpect.child.buffer after 1 sec sleep, the moving fwd to normal 
		expect.
		'''

		if self.prompt_line != '':
			cmd = cmd.strip()

			self.print_debug_message('-'*20+'buffer'+'-'*20+'\n' + \
				self.child.buffer+'+'*40+'\n',1)

			if cmd in self.child.buffer:
				start = self.child.buffer.index(cmd)
				#print 'buffer, start---->', start
				self.child.buffer = self.child.buffer[start:]
			# chop off the leading contents before cmd

			self.print_debug_message('-'*20+'before'+'-'*20+'\n' + \
				self.child.before+'+'*40+'\n',1)
			if cmd in self.child.before:
				start = self.child.before.index(cmd)
				#print 'before, start---->', start
				self.child.before = self.child.before [start:]
			
			#print '#'*80, self.child.buffer, '#'*80
			self.print_debug_message('~'*40+'\n'+self.child.buffer+':'*40+'\n',9)

	def expect(self, prompt_list='', timeout=DEFAULT_SHORT_TIMEOUT):
		'''
		local expect wrapper with common exception handling
		'''

		if prompt_list == '':
			prompt_list = self.prompt_list

		#print 'expect buffer==>', self.child.buffer

		#if type(self.child.after) is str: 
		#	pprint_message('self.child.after@expect', self.child.after)
	
		try: 
			return self.child.expect(prompt_list, timeout=timeout), \
				self.child.before + self.child.after
		except pexpect.EOF:
			self.print_debug_message('Received EOF', 1)
		except pexpect.TIMEOUT:
			self.print_debug_message('Session Timeout', 0)
			pprint_message('expected prompt list', '\n'.join(prompt_list))

		#
		# print detailed debug 
		#
		self.print_debug_message('-----------------------------------', 2)
		self.print_debug_message('prompts : %s' % ' | '.join(prompt_list), 2)
		self.print_debug_message(str(self.child), 9)

		return -1, ''

	def sendln_expect(self, cmd, prompt_list='', 
		timeout=DEFAULT_SHORT_TIMEOUT):
		'''
		local expect wrapper with common exception handling
		'''

		if len(cmd):
			self.sendline(cmd)
			#self.chop_off_buffer(cmd)


		# if no given prompt_list, use the default self.prompt_list
		if prompt_list == '':
			prompt_list = self.prompt_list

		i, o = self.expect(prompt_list, timeout)

		self.print_debug_message('\n%s sendln_expect %s\n[%d]\n[%s]\n%s' % ('-'*10, 
			'-'*10, i, o, '-'*35), 3)

		return i,o

	def enable(self):
		'''
		enter into enable mode
		'''
		self.print_debug_message('\ntry to enter enable mode', 9)
	
		index, output = self.sendln_expect('enable', ['#', 'assword:'])

		#
		# no enable password, directly into enable mode
		#
		if index == 0: 
			self.print_debug_message('successfully enter enable mode', 9) 
			return 1
		#
		# receive P|password to ask for enable_password
		#
		elif index == 1: 
			index2, output = self.sendln_expect(self.enable_password, ['#']) 
				
			if index2 == 0: 
				self.print_debug_message('successfully enter enable mode', 9)
				return 1
	
		return -1

	def connect(self, enable_mode=1):
		'''
		initial connection to router, exited after reaching enabled mode
		if enable_mode=1
		'''

		#
		# spawn a session with provided connection info
		#
		self.child = pexpect.spawn(self.conn, maxread=MAX_READ)
		self.child.logfile_read = sys.stdout

		#
		# 1st send a \r\n, then check 5 possible prompts
		#
		index, o = self.sendln_expect('', 
			['yes/no', 'sername:', 'assword:', '>', '#', '\$'])

		#pprint_message('', 'EXPECT1==>%d' % index)

		#
		# child return output -> 'yes/no', asking confirmation of DSA key
		#
		if index == 0:
			self.print_debug_message('connect_0: be asked for SSH key', 2)

			index, o = self.sendln_expect('yes', 
				['yes/no', 'sername:', 'assword:', '>', '#', '\$'])

			if index == 0:
				self.print_debug_message('connect_0: error for SSH key', 0)
				return -1
		
		#
		# child return output -> 'U|username:', providing login credentials
		#
		if index == 1:
			self.print_debug_message('connect_1: be asked for user', 2)

			index, o = self.sendln_expect(self.user, 
				['yes/no', 'sername:', 'assword:', '>', '#', '\$'])
			
			if index < 2:
				self.print_debug_message('connect_1: error for user', 0)
				return -1
		
		#
		# child return output -> 'P|password', providing password
		#
		if index == 2:
			self.print_debug_message('connect_2: be asked for password', 2)

			#pprint_message('', 'password==>%s' % self.password)
			index, o = self.sendln_expect(self.password, 
				['yes/no', 'sername:', 'assword:', '>', '#', '\$'])

			if index < 3:
				self.print_debug_message('connect_2: error for password', 0)
				return -1
		
		# 
		# child return output -> '>', means login router but not into enable 
		# mode
		#
		if index == 3: 
			self.print_debug_message('connect_3: login but not enable mode',
				2)

			# prompt '>' means it is a router
			self.device = 'router'

			if enable_mode:
				# if conn must exit in enabled mode, go aheand for enable()
				if self.enable() == -1:
					self.print_debug_message('connect_3: failed to enter \
						enable mode', 2)
					return -1

		#
		# child return output -> '#', means directly into enable mode
		#
		if index == 4: 
			self.print_debug_message('connect_4: login enable mode', 2)

			# prompt '>' means it is a router
			self.device = 'router'

		#
		# child return output -> '$', means it is a linux box
		#
		if index == 5: 
			self.print_debug_message('connect_5: login linux/pc', 2)

			# prompt '$' means it is a router
			self.device = 'pc'

		self.print_debug_message('connect: successufly login router', 1)
		
		return 1

	def page_off(self):
		#
		# At this time, we don't know the type of device/OS, unless 
		# it was pre-set by parameter passed thru. If self.os=='', we
		# send both commands
		#
		if self.os == '' or re.search('cisco|ios', self.os, re.IGNORECASE): 
			self.sendln_expect('terminal len 0')

		if self.os == '' or re.search('brocade|netiron', self.os, 
			re.IGNORECASE): 
			self.sendln_expect('skip')

	def parse_prompt(self):
		'''
		send an empty newline, the last time of output is full prompt
		'''
		i, o = self.sendln_expect('\n')

		self.prompt_line = o.split('\n')[-1].strip()

		self.prompt_list = [self.prompt_line]

		a = re.search('^([^\n]+)([#|>|\$])\s*$', self.prompt_line)

		if a:
			self.hostname, self.prompt_char = a.groups()

			if self.prompt_char == '$':
				self.prompt_char == '\\$'

			self.prompt_line = '%s[^\n]*%s' % (self.hostname, 
				self.prompt_char)

			self.prompt_list = [self.prompt_line]
		else:
			self.print_debug_message('unexpected hostname and prompt - [%s]' % \
				self.prompt_line, 1)

		self.print_debug_message('pyconsole.parse_prompt->promplist: %s' % 
			'|'.join(self.prompt_list), 3)

	def post_connect(self):
		'''
		1) Turn display page mode off.  
		   * Cisco devices - "terminal length 0"; 
		   * Brocade devices - "skip"
		2) Fetch the device prompt
		'''

		if self.device == 'router': 
			self.page_off()

		self.parse_prompt()

	def collect_sysinfo(self):
		'''
		After connection established, do "show version" which works on most
		of network devices to collect system inforamtion, like vendor, os and
		version. 	
		'''
		pass

	def run_commands(self, cmds, timeout=DEFAULT_SHORT_TIMEOUT):
		output = ''
		for cmd in cmds.split('\n'):
			self.print_debug_message('\n%s\nrun_commands->%s\n%s' % ('-'*50,cmd,'-'*50),9)
			i, _output = self.sendln_expect(cmd, timeout=timeout)
			output += _output
		
		self.print_debug_message(str(self.child), 9)

		return output

	def close(self):
		self.child.close()

#/ -------------------------- shared functions ------------------------------ \
#| pprint_message(subject, message): pretty print message                     |
#| get_ping_pert(output): get ping success rate from router/pc        |
#\ -------------------------------------------------------------------------- /

def pprint_message(subject, message):
	'''
	pretty print the message, like
	/------------- subject -------------------\
	|text message line 1...                   |
	|text message line 2...                   |
	\-----------------------------------------/
	'''

	# preset the line len to len(subject) = 6, so
	# /- SSSSSSSSSSSubjectttttttttt -\
	# | line 1                       |
	# \------------------------------/
	subject = subject.strip()
	max_line_len = len(subject) + 6

	# find the max len of message line
	for line in message.split('\n'):
		if len(line.rstrip()) + 4 > max_line_len:
			max_line_len = len(line.rstrip()) + 4

	# if len is odd, change it to even
	if max_line_len % 2:
		max_line_len += 1

	# print the 1st line
	_len_hyphen = (max_line_len - len(subject) - 4)/2
	print '\n/', '-'*_len_hyphen, subject, '-'*_len_hyphen, '\\'

	# print message lines:
	for line in message.split('\n'):
		line = line.rstrip()
		print '|', line, ' '*(max_line_len - 3 - len(line)), '|'

	# print last line
	print '\\', '-'*(max_line_len-2), '/'

def get_ping_pert(output):
	'''
	parse ping command output and fetech ping pass percentage. now this
	function supports:
	1) Brocade NetIron 5.x
	2) Linux Ubunbu 14.x
	'''

#	'''Brocade NetIron 5.x'''
#	telnet@NIRouter#ping 1.1.1.1
#	Sending 10, 16-byte ICMP Echo to 1.1.1.1, timeout 5000 msec, TTL 64
#	Type Control-c to abort
#	Reply from 1.1.1.1         : bytes=16 time<1ms TTL=64
#	.....
#	Success rate is 100 percent (10/10), round-trip min/avg/max=0/0/0 ms.
#	                ^^^ =====> !!!!!!!!!!!!!!!!!
#
#	'''PC/Ubuntun/14.x'''
#	user@UBUNTU:~$ ping 1.1.1.1 -c 5 -i 0.5
#	PING 1.1.1.1 (1.1.1.1) 56(84) bytes of data.
#	....
#	64 bytes from 1.1.1.1: icmp_seq=5 ttl=63 time=0.590 ms
#	--- 1.1.1.1 ping statistics ---
#	5 packets transmitted, 5 received, 0% packet loss, time 1998ms
#	                                   ^^ ===> !!!!!!!!!!!!
	
	pert = -1

	for line in output.split('\n'): 
		a = re.search('Success rate is (\d+) percent', line) 
		if a: 
			pert = int(a.group(1))
		
		b = re.search('(\d+)% packet loss', line)
		if b: 
			pert = 100- int(b.group(1))

	if pert == -1:
		pprint_message('get_ping_pert failed to get ping %', output)

	return pert 

def psleep(num_sec):
	'''
	pretty sleep
	'''

	if num_sec < 0:
		return 0

	print '\nsleeping %d seconds:' % num_sec
	for i in range(num_sec):
		if i % 10 == 0:
			print '\nsec:%4d' % i,
		time.sleep(1)
		print '.',
		sys.stdout.flush()
	print '\n'
