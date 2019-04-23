# Copyright (c) 2019 Carleton University Broadband Networks Laboratory

import os
import select

class Attenuator:
	def __init__(self, dev=None):
		# device configurations
		self.__model = "Unknown Model"
		self.__max_attn = 0
		self.__def_step = 0
		self.__freq = "0-0GHz"

		self.__tout = 1.0	# device read timeout
		self.__dev = dev
		self.__status = self.__initDevice()

	"""
		private API
	"""

	def __initDevice(self):
		if self.__dev is not None:
			try:
				self.tty = os.open(self.__dev, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
			except:
				return False
			if not self.__reset():
				return False
			self.__readConfig()
			return True
		return False

	def __reset(self):
		if not self.__disableConsole():
			return False
		if not self.__clear():
			return False
		if not self.__test():
			return False
		return True

	def __disableConsole(self):
		return self.__progQuery("CONSOLE DISABLE")

	def __resetHard(self):
		self.__program("*RST")		# perform reset

	def __test(self):
		return self.__progQuery("*TST")	# perform test

	def __clear(self):
		return self.__progQuery("*CLS")	# clear error status

	def __readConfig(self):
		q = self.__query("RFCONFIG?")
		conf = [x.strip() for x in q.split(',')]
		if len(conf) == 4:
			self.__model = conf[0] 
			self.__max_attn = float(conf[1])
			self.__def_step = float(conf[2])
			self.__freq = conf[3]
			return True
		return False
		

	# send messages to the device
	def __send(self, msg):
		os.write(self.tty, msg.encode('ascii'))

	# receive response line from the device
	def __recv(self):
		line = ''
		while self.tty in select.select([self.tty], [], [], self.__tout)[0]:
			b = os.read(self.tty, 1)
			if b and b is not '\n':
				line += b.decode('ascii')
			else:
				break
		return line.rstrip()

	# send program commands to the device
	def __program(self, cmd):
		if self.tty is not None:
			self.__send(cmd + "\n")

	# send query commands to the device
	def __query(self, cmd):
		if self.tty is not None:
			self.__send(cmd + "\n")
			return self.__recv()
		return None

	# send program commands to the device and wait for success
	def __progQuery(self, cmd):
		cmd += ";*OPC?"
		if self.tty is not None:
			q = self.__query(cmd)
			return '1' in q
		return False


	"""
		public API
	"""

	# is the device ready?
	def ready(self):
		return self.__status

	# set the attenuation level to value
	def setAttenuation(self, value=0):
		if value > self.__max_attn:
			return False
		cmd = "ATTN " + str(value)
		#self.__program(cmd)
		return self.__progQuery(cmd)

	# get the current attenuation level from the device
	def getAttenuation(self):
		return float(self.__query("ATTN?"))

	# set the attenuation step size to stepsize
	def setStepSize(self, stepsize=0):
		cmd = "STEPSIZE " + str(stepsize)
		#self.__program(cmd)
		return self.__progQuery(cmd)

	# get the current attenuation step size from the device
	def getStepSize(self):
		return float(self.__query("STEPSIZE?"))

	# increment current attenutation value by current step size
	def increment(self):
		#self.__program("INCR")
		return self.__progQuery("INCR")

	# decrement current attenutation value by current step size
	def decrement(self):
		#self.__program("DECR")
		return self.__progQuery("DECR")

	# get device model
	def getModel(self):
		return self.__model

	# get device max attenuation value
	def getMaxAttn(self):
		return self.__max_attn

	# get device default step size value
	def getDefStepSize(self):
		return self.__def_step

	# get device frequency
	def getFrequency(self): 
		return self.__freq



"""
	TEST
"""
if __name__ == "__main__":
	attn = Attenuator("/dev/ttyACM0")
	print("Trying /dev/ttyACM0") 
	if attn.ready():
		print("Device connected successfully.")
	else:
		print("Error: no such device.")
		exit(1)

	print("")

	# device information
	print("Device model: " + attn.getModel())
	print("Device max attenuation: " + str(attn.getMaxAttn()))
	print("Device default step size: " + str(attn.getDefStepSize()))
	print("Device frequency: " + attn.getFrequency())

	print("")

	# set attentuation to 10.0
	if attn.setAttenuation(10.0):
		print("setAttenuation: SUCCESS")
	else:
		print("setAttenuation: FAILED")
	print(("Attenuation: " + str(attn.getAttenuation())))

	if attn.setStepSize(2):
		print("setStepSize: SUCCESS")
	else:
		print("setStepSize: FAILED")

	if attn.increment():
		print("increment: SUCCESS")
	else:
		print("increment: FAILED")
	print(("Attenuation: " + str(attn.getAttenuation())))

	if attn.decrement():
		print("decrement: SUCCESS")
	else:
		print("decrement: FAILED")
	print(("Attenuation: " + str(attn.getAttenuation())))
