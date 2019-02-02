import numpy as np
import matplotlib.pyplot as plt
import numpy
import math
import sys


# Input arguments:
# ----------------
# device_name (string): the name of the device under test
# file_name (string): the path of the .bin file containing the USRP data
# access_category (string): the type of service -> voice, video, best_effort, back_ground
# sampling_rate (int): sampling rate of the USRP
# duration (float): time interval of the data captured in seconds, default 2.5 seconds


class ANTS_Plotter():

    def __init__(self, access_category, test_name, sample_rate=20e6):

        self.test_name = test_name
        self.access_category = access_category
        self.file_name = self.test_name + "_" + self.access_category + ".bin"
        self.sample_rate = sample_rate
        self.output_file_name = self.test_name + "_" + self.access_category + "_results.txt"

        if self.access_category == "video":
        	self.txop_limit = 4
        	self.aifs = 34
        	self.n = 8
        	self.kp1 = 9
        	self.mind = 32
        	self.maxd = 95
        elif self.access_category == "best_effort":
        	self.txop_limit = 6
        	self.aifs = 43
        	self.n = 16
        	self.kp1 = 17
        	self.mind = 41
        	self.maxd = 176
        elif self.access_category == "background":
        	self.txop_limit = 6
        	self.aifs = 79
        	self.n = 16
        	self.kp1 = 17
        	self.mind = 77
        	self.maxd = 212
        else: # default to "voice" access category
        	self.txop_limit = 2
        	self.aifs = 34
        	self.n = 4
        	self.kp1 = 5
        	self.mind = 32
        	self.maxd = 59

    # open the data file and read the raw data from it
    def read_and_parse(self, filename=None):

        if filename == None:
            filename = self.file_name

        print("The plotter file name is {0}\n".format(self.file_name))

        with open(filename, mode='rb') as file:
            self.raw_data = np.fromfile(file, dtype=np.float32)
        file.close()
        file_length = len(self.raw_data)

        # In-phase data is at the even indices, quadrature is at the odd ones
        self.in_phase_data = self.raw_data[0:file_length:2]
        self.quadrature_data = self.raw_data[1:file_length:2]
        # Find the common length of the two data subsets to ensure proper plots
        self.data_length = min(len(self.in_phase_data), len(self.quadrature_data))
        self.duration = self.data_length/self.sample_rate

        self.in_phase_data = self.in_phase_data[0:self.data_length]
        self.quadrature_data = self.quadrature_data[0:self.data_length]

    # This is the core data processing function. It may be worth splitting it up further
    def setup_packet_data(self, duration=None, data_length=None, noise_threshold=0.02):

        if duration == None:
            duration = self.duration

        if data_length == None:
            data_length = self.data_length

        # set the time axis from the data length and the total duration
        self.time = np.linspace(0, duration, num=data_length)
        # combine inphase and quadrature components as a complex number, cos(wt) + 1j*sin(wt)
        self.complex_data = self.in_phase_data + (1j*self.quadrature_data)
        self.power_data = abs(self.complex_data)**2
        self.threshold = noise_threshold * np.mean(self.power_data)

        # disregard the fluctuations of the signal in the packet
        self.packet_indices = np.concatenate(np.where(self.power_data > self.threshold))

        # possible wait time between packets in seconds
        self.wait_time = 4e-6
        # number of samples from the start of the packet to safely assume that the packet is complete but before the arrival of the next packet
        self.window_size = int(self.sample_rate*self.wait_time)

        temp_vector = np.diff(self.packet_indices)
        temp_vector_length = len(temp_vector)
        temp_indices = np.concatenate(np.where(temp_vector > self.window_size))

        # an array to store the indices of the end of the packet
        self.packet_end_indices = np.array([0]*(len(temp_indices)+1))
        self.packet_end_indices[0:(len(temp_indices)):1] = self.packet_indices[temp_indices]
        self.packet_end_indices[len(temp_indices)] = self.packet_indices[-1]

        # an array to store the indices of the start of the packet
        self.packet_start_indices = np.array([0]*(len(temp_indices)+1))
        self.packet_start_indices[1:(len(temp_indices)+1):1] = self.packet_indices[temp_indices+1]
        self.packet_start_indices[0] = self.packet_indices[0]

        # calculate the number of packets received
        self.number_of_packets = len(self.packet_start_indices)
        # sort the indices of the end of the packet in an ascending order

        self.packet_indicator = np.zeros([data_length, 1])
        self.packet_indicator[self.packet_start_indices] = 1
        self.packet_indicator[self.packet_end_indices] = 1

        # calculate the interframe spacing by finding the time difference between the end and the start of each consecutive packets (in microseconds)
        self.interframe_spacing = (1e6/self.sample_rate)*(self.packet_start_indices[1:]-self.packet_end_indices[0:-1])
        self.packet_duration = (1e6/self.sample_rate)*(self.packet_end_indices-self.packet_start_indices)

        self.interframe_spacing_length = len(self.interframe_spacing)
        self.COT = np.where(self.interframe_spacing > 25)
        self.COT = np.asarray(self.COT).T

        self.packet_indices = np.concatenate(np.where(self.power_data > self.threshold)) #added
        self.SIFSD = np.concatenate(np.where(self.interframe_spacing <= 20.5))
        self.correct_back_off = np.concatenate(np.where(self.interframe_spacing > 27))
        self.txop_durations = []
        self.COT_length = len(self.COT)

        for i in range(1, self.COT_length):
        	a = (1e3 / self.sample_rate) * (self.packet_end_indices[self.COT[i]] - self.packet_start_indices[self.COT[i - 1] + 1])
        	if a != 0:
        		self.txop_durations.append(a)
        self.txop_durations = np.concatenate(self.txop_durations)

        self.min_back_off = min(self.interframe_spacing)
        self.mean_txop = np.mean(self.txop_durations)
        self.max_txop = np.max(self.txop_durations)

        self.packet_durations = (1e6 / self.sample_rate) * (self.packet_end_indices - self.packet_start_indices)
        self.max_packet_duration = max(self.packet_durations)/1e3

        if self.txop_limit == 0:
        	self.violating_durations = self.txop_durations[np.concatenate(np.where(self.txop_durations > self.max_packet_duration))]
        else:
        	self.violating_durations = self.txop_durations[np.concatenate(np.where(self.txop_durations > self.txop_limit))]
        self.txop_factor = (len(self.violating_durations)/len(self.txop_durations))


        self.slot_time = 9
        self.BFmin = self.aifs - self.slot_time/2
        self.BFmax = self.aifs + self.slot_time*(self.n-1) + self.slot_time/2
        self.BFmid = (self.BFmax + self.BFmin)/2

        self.back_offs = self.interframe_spacing[self.correct_back_off]
        self.blen = len(self.back_offs)
        self.b = np.asarray(np.zeros(self.n))
        self.b2 = np.asarray(np.zeros(self.kp1))

        for i in range(0, self.blen):
        	x = self.back_offs[i]
        	if x <= self.BFmin:
        		self.b[0] = self.b[0] + 1
        	elif x >= self.BFmax:
        		self.b[self.n-1] = self.b[self.n-1] + 1
        	else:
        		index = math.ceil((x-self.BFmin)/self.slot_time)-1
        		self.b[index] = self.b[index] + 1

        	if x < self.mind:
        		self.b2[0] = self.b2[0] + 1
        	elif x >= self.maxd:
        		self.b2[self.kp1-1] = self.b2[self.kp1-1] + 1
        	else:
        		index = math.ceil((x-self.mind)/self.slot_time)
        		self.b2[index] = self.b2[index] + 1

        self.prob = self.b/sum(self.b)
        self.nz_prob = self.prob[np.where(self.prob > 0)]
        self.kbl = -sum(np.multiply(self.nz_prob, np.log10(self.nz_prob/(1/self.n))))
        self.dist_factor = 1 - np.exp(self.kbl)
        self.kk = numpy.arange((self.n - 1)/2, - (self.n - 1)/2-1, -1)
        accum = sum(np.multiply(self.b, self.kk))
        avrg = accum / self.blen
        mid = (self.n-1)/2
        self.ag_factor = avrg/mid
        self.SIFSs = self.interframe_spacing[np.where(self.interframe_spacing < 16 + 9/2)]
        self.SIFSs = self.SIFSs[np.where(self.SIFSs > 4)]
        self.sifs_factor = (np.mean(self.SIFSs) - 16)/16

        # Norm Factor
        self.norm_factor = math.sqrt(self.ag_factor**2 + self.txop_factor**2 + self.dist_factor**2 + self.sifs_factor**2)/2
        self.norm_factor_percent = (1 - self.norm_factor)*100

        # Geometric mean Factor
        self.geometric_factor = ((1 - abs(self.ag_factor)) * (1 - self.txop_factor) * (1 - self.dist_factor) * (1 - abs(self.sifs_factor)))**(1/4)

        # Calculate the observed cumulative probabilities (p)
        self.e = self.blen  # total observed periods
        self.p = np.asarray(np.zeros(self.kp1))
        self.p_max = np.asarray(np.zeros(self.kp1))

        for i in range(0, self.kp1):
            self.p[i] = sum_range(self.b2, 0, i)/self.e

        self.p_max[0] = 0.05
        self.p_max[self.kp1 - 1] = 1

        if self.access_category == "voice":
        	for i in range(1, 4):
        		self.p_max[i] = self.p_max[0] + i * 0.25
        elif self.access_category == "video":
        	self.p_max[1] = 0.18
        	for i in range(2, 7):
        		self.p_max[i] = self.p_max[1] + (i - 1) * 0.125
        	self.p_max[self.kp1 - 2] = 1
        elif self.access_category == "best_effort" or self.access_category == "background":
        	self.p_max[1] = 0.12
        	for i in range(2, 16):
        		self.p_max[i] = self.p_max[1] + (i - 1) * 0.0625
        else:
        	for i in range(1, 4):
        		self.p_max[i] = self.p_max[0] + i * 0.25

    def write_results_to_file(self):
        with open(self.output_file_name, "w") as outfile:

            outfile.write("Found " + str(len(self.packet_end_indices)) + " packets, " + str(len(self.interframe_spacing)) + " IFSs"+"\n")
            outfile.write("minBackOff: " + str(self.min_back_off)+"\n")
            outfile.write("meanTxop: " + str(self.mean_txop)+"\n")
            outfile.write("maxTxop: " + str(self.max_txop)+"\n")
            outfile.write("TxopFactor: " + str(self.txop_factor)+"\n")
            outfile.write("KBL: " + str(self.kbl)+"\n")
            outfile.write("DistFactor: " + str(self.dist_factor)+"\n")
            outfile.write("AGFactor: " + str(self.ag_factor)+"\n")
            outfile.write("SIFSFactor: " + str(self.sifs_factor)+"\n")
            outfile.write("NF: " + str(self.norm_factor)+"\n")
            outfile.write("GF: " + str(self.geometric_factor)+"\n")

            # print results to debug console
            print("Found " + str(len(self.packet_end_indices)) + " packets, " + str(len(self.interframe_spacing)) + " IFSs")
            print("minBackOff: " + str(self.min_back_off))
            print("meanTxop: " + str(self.mean_txop))
            print("maxTxop: " + str(self.max_txop))
            print("TxopFactor: " + str(self.txop_factor))
            print("KBL: " + str(self.kbl))
            print("DistFactor: " + str(self.dist_factor))
            print("AGFactor: " + str(self.ag_factor))
            print("SIFSFactor: " + str(self.sifs_factor))
            print("NF: " + str(self.norm_factor))
            print("GF: " + str(self.geometric_factor))

            if self.ag_factor > 0:
                print(str(abs(self.ag_factor)*100) + " Aggressive and " + str(self.norm_factor_percent) + " Compliant")
                outfile.write(str(abs(self.ag_factor) * 100) + " Aggressive and " + str(self.norm_factor_percent) + " Compliant"+"\n")
            else:
                print(str(abs(self.ag_factor) * 100) + " Submissive and " + str(self.norm_factor_percent) + " Compliant")
                outfile.write(str(abs(self.ag_factor) * 100) + " Submissive and " + str(self.norm_factor_percent) + " Compliant"+"\n")
        outfile.close()

    def plot_results(self):

        # generate a plot for the power of the signal and the packet indicators
        plt.figure(1)
        plt.plot(self.time, np.sqrt(self.power_data), 'b-', self.time, self.packet_indicator, 'r-')#, time, packet_indicator, 'r-')
        plt.title("Plot of the magnitude of the signal vs Time")
        plt.xlabel("Time (sec)")
        plt.ylabel("Signal magnitude") #find out if the power is in Watts or dB?
        plt.draw()
        plt.savefig(self.test_name + '_' + self.access_category + '_signal_magnitude_plot.png')

        plt.figure(2)
        plt.xlim((0,300))
        plt.hist(self.interframe_spacing, bins=500)
        plt.title("Histogram of the inter-frame spacing")
        plt.xlabel("Inter-frame spacing (microsecond)")
        plt.ylabel("Frequency")
        plt.draw()
        plt.savefig(self.test_name + '_' + self.access_category + '_interframe_spacing_histogram.png')

        plt.figure(3)

        plt.hist(self.txop_durations, bins=100)
        plt.title("Histogram of the Txop durations")
        plt.xlabel("Txop duration (milli second)")
        plt.ylabel("Frequency")
        plt.draw()
        plt.savefig(self.test_name + '_' + self.access_category + '_txop_durations_histogram.png')

        plt.figure(4)
        t = np.linspace(0, self.kp1-1, num=self.kp1)
        plt.bar(t, self.p, color='b', width=0.25)
        plt.bar(t+0.25, self.p_max, color='r', width=0.25)
        plt.title("Bin Probability and Threshold")
        plt.xlabel("Bin")
        plt.ylabel("Probability")
        Gender = ['Bin Probability', 'Compliance Upper threshold']
        plt.legend(Gender, loc=2)
        plt.draw()
        plt.savefig(self.test_name + '_' + self.access_category + '_bin_probability.png')

        #plt.show(block=False)


def sum_range(l,a,b):
	sum = 0
	for i in range(a, b+1,1):
		sum += l[i]
	return sum
