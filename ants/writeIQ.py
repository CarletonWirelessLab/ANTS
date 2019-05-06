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

USBDEVFS_RESET = ord('U') << (4*2) | 20

class WriteIQ(gr.top_block):
	def __init__(self, runFor, center_frequency, gain, file_name):
		gr.top_block.__init__(self)
		
		# Define variables
		sample_rate = 20e6
		bandwidth = 20e6
		antenna = "RX2"
		file_name = file_name

		# Define blocks
		# 1) USRP Source
		self.usrpSource = uhd.usrp_source(",".join(("", "")), uhd.stream_args(cpu_format="fc32", channels=range(1)))
		print('Set sample rate to', sample_rate)
		self.usrpSource.set_samp_rate(sample_rate)
		print('Set center frequency to', center_frequency)
		self.usrpSource.set_center_freq(center_frequency, 0)
		print('Set gain to', gain)
		self.usrpSource.set_gain(gain, 0)
		print('Set antenna to', antenna)
		self.usrpSource.set_antenna(antenna, 0)
		print('Set bandwidth to', bandwidth)
		self.usrpSource.set_bandwidth(bandwidth, 0)

		# 2) File Sink
		self.fileSnk = blocks.file_sink(gr.sizeof_gr_complex*1, file_name, False)
		print('Write IQ samples to', file_name)

		# Define connections
		self.disconnect_all()
		self.connect((self.usrpSource, 0), (self.fileSnk, 0))

def main():
	file_name = sys.argv[1]
	runFor = float(sys.argv[2]) # sec
	center_frequency = float(sys.argv[3])*1e9
	gain = int(sys.argv[4])
	
	writeIq = WriteIQ(runFor, center_frequency, gain, file_name)
	t = threading.Thread(target=writeIq.run)
	t.daemon = True
	t.start()
	time.sleep(runFor)
	writeIq.stop()
	print('Finished sampling for',runFor,'s')

	quit()

if __name__ == '__main__':
	main()
