#!usr/bin/env python2

# Author: Kareem Attiah/ Ammar Alhosainy
# Date: Nov 15th, 2017/ March 3rd, 2018

from gnuradio import gr
from gnuradio import uhd
from gnuradio import blocks
import sys
import threading
import time

global name 
global runFor #sec

class writeIQ(gr.top_block):

	def __init__(self):
		gr.top_block.__init__(self)
		
		global name, runFor

		# Define variables and their default values
		self.samp_rate = self.cbw = 20e6
		self.gain = 50
		self.cfreq = 5.765e9 #2.412e9
		self.antenna = "RX2"
		self.file_name = 'AP11_2018_to_AsusUsb42_QoS_100M_0x' + name +'.bin'

		# Define blocks
		# 1) USRP Block
		self.usrpSource = uhd.usrp_source(
        		",".join(("", "")),
        		uhd.stream_args(
        			cpu_format="fc32",
        			channels=range(1),
        		),
        	)
		
		# 2) Set default parameters
		self.usrpSource.set_samp_rate(self.samp_rate)
        	self.usrpSource.set_center_freq(self.cfreq, 0)
        	self.usrpSource.set_gain(self.gain, 0)
        	self.usrpSource.set_antenna(self.antenna, 0)
        	self.usrpSource.set_bandwidth(self.cbw, 0)


		# 2) File Sink
		self.fileSnk = blocks.file_sink(gr.sizeof_gr_complex*1, self.file_name, False)


		# Define connections
		self.connect((self.usrpSource, 0), (self.fileSnk, 0))

	def get_samp_rate(self):
        	return self.samp_rate

    	def set_samp_rate(self, samp_rate):
        	self.samp_rate = samp_rate
        	self.usrpSource.set_samp_rate(self.samp_rate)

    	def get_gain(self):
        	return self.gain

    	def set_gain(self, gain):
        	self.gain = gain
		self.usrpSource.set_gain(self.gain, 0)

    	def get_cfreq(self):
        	return self.center_frequency

    	def set_cfreq(self, cfreq):
        	self.cfreq = cfreq
        	self.usrpSource.set_center_freq(self.cfreq, 0)

	def get_cbw(self):
		return self.cbw

	def set_cbw(self, cbw):
		self.cbw = cbw
		self.usrpSource.set_bandiwdth(self.cbw, 0)


def dowork():
	classInst = writeIQ()
	classInst.run()

def main():

	global name, runFor
	name = '0'
	runFor = 2.5 # sec
	if len(sys.argv) > 1:
		name   = sys.argv[1]
		runFor = float(sys.argv[2]) #sec

	t = threading.Thread(target=dowork)
	t.daemon = True 
	t.start()
	#time.sleep(1.9828)   #to initiate the device on HP laptop 
	time.sleep(runFor)
	print '## END READING ## Duration =',runFor,' s'
	quit()

if __name__  == '__main__':
	main()


