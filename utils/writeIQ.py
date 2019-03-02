#!usr/bin/env python2

# Authors: Kareem Attiah/ Ammar Alhosainy
# Date: Nov 15th, 2017/ March 3rd, 2018

from gnuradio import gr
from gnuradio import uhd
from gnuradio import blocks
import sys
import threading
import time
import os
from fcntl import ioctl

global name
global runFor #sec
global access_category

global classInst
USBDEVFS_RESET = ord('U') << (4*2) | 20

class writeIQ(gr.top_block): 
	def __init__(self):
		gr.top_block.__init__(self)
		global name, runFor, access_category
		self.disconnect_all()
		# Define variables and their default values
		self.samp_rate = 20e6
		self.cbw = 20e6
		self.gain = 60
		self.cfreq = 5.765e9 #2.412e9
		self.antenna = "RX2"
		self.file_name = name + '_' + access_category + '.bin'
		print(self.file_name)
		
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
		self.disconnect_all()
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
	classInst.run()
	print "EXIT RUN"
    
def main():
	global name, runFor, access_category
	global classInst
        
	name = sys.argv[1]
	runFor = float(sys.argv[2]) # sec
	access_category = sys.argv[3]
	file_name = name + '_' + access_category + '.bin'
	classInst = writeIQ()
	t = threading.Thread(target=dowork)
	t.daemon = True
	t.start()
	time.sleep(runFor)
	classInst.stop()
	print '## END READING ## Duration =',runFor,' s'

	time.sleep(2)
	quit()

if __name__  == '__main__':
	main()
