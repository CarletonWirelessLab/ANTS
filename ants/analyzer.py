import math
import os
import re
import sys
from textwrap import dedent

import matplotlib.pyplot as plt
import numpy as np

class IQSamplesFile():
    def __init__(self, iq_samples_file_name, sample_rate = 20e6, noise_threshold = 0.02):
        match = re.search("iqsamples_(video|voice|best_effort|background)_run(\d+)\.bin", iq_samples_file_name)
        if not match:
            raise Exception("ERROR: Could not parse file name {} to ac and run#".format(iq_samples_file_name))
        self.access_category = match.group(1)
        self.run = match.group(2)

        print("Loading {}...".format(iq_samples_file_name))
        with open(iq_samples_file_name, mode='rb') as file:
            raw_data = np.fromfile(file, dtype=np.float32)
        file_length = len(raw_data)
        
        # In-phase data is at the even indices, quadrature is at the odd ones
        in_phase_data = raw_data[0:file_length:2]
        quadrature_data = raw_data[1:file_length:2]
        # Find the common length of the two data subsets to ensure proper plots
        data_length = min(len(in_phase_data), len(quadrature_data))
        duration = data_length/sample_rate

        in_phase_data = in_phase_data[0:data_length]
        quadrature_data = quadrature_data[0:data_length]

        print("Found {} samples, corresponding to a duration of {}s".format(data_length, duration))

        # set the time axis from the data length and the total duration
        self.time = np.linspace(0, duration, num=data_length)
        # combine inphase and quadrature components as a complex number, cos(wt) + 1j*sin(wt)
        complex_data = in_phase_data + (1j*quadrature_data)
        self.power_data = abs(complex_data)**2
        #self.power_data = power_data[int(len(power_data)/100):-1]
        threshold = noise_threshold * np.mean(self.power_data)

        # disregard the fluctuations of the signal in the packet
        packet_indices = np.concatenate(np.where(self.power_data > threshold))
        # possible wait time between packets in seconds
        wait_time = 4e-6
        # number of samples from the start of the packet to safely assume that the packet is complete but before the arrival of the next packet
        window_size = int(sample_rate*wait_time)
        temp_vector = np.diff(packet_indices)
        temp_indices = np.concatenate(np.where(temp_vector > window_size))

        # an array to store the indices of the end of the packet
        self.packet_end_indices = np.array([0]*(len(temp_indices)+1))
        self.packet_end_indices[0:(len(temp_indices))] = packet_indices[temp_indices]
        self.packet_end_indices[len(temp_indices)] = packet_indices[-1]

        # an array to store the indices of the start of the packet
        self.packet_start_indices = np.array([0]*(len(temp_indices)+1))
        self.packet_start_indices[1:(len(temp_indices)+1)] = packet_indices[temp_indices+1]
        self.packet_start_indices[0] = packet_indices[0]

        self.packet_indicator = np.zeros([data_length, 1])
        self.packet_indicator[self.packet_start_indices] = 1
        self.packet_indicator[self.packet_end_indices] = 1
    
    def plot(self, start = 0, num_samples = -1, filename = None):
        plt.figure()
        plt.plot(self.time[start:num_samples], np.sqrt(self.power_data[start:num_samples]), 'b-', self.time[start:num_samples], self.packet_indicator[start:num_samples], 'r-')
        plt.title("Plot of the magnitude of the signal vs Time")
        plt.xlabel("Time (sec)")
        plt.ylabel("Signal magnitude") #find out if the power is in Watts or dB?

        if filename is None:
            plt.show()
        else:
            plt.draw()
            plt.savefig(filename)
            plt.close()    

class ANTS_Analyzer():
    class Stats():
        def __init__(self, count, min, mean, max, violations):
            self.count = count
            self.min = min
            self.mean = mean
            self.max = max
            self.violations = violations
        
    class Results():
        def __init__(self):
            self.interframe_spacing = None
            self.number_of_packets = None
            self.txop_durations = None
            self.txop_stats = None
            self.backoff_stats = None
            self.backoff_bin_probabilities = None

            self.access_category = None
            self.txop_limit = None
            self.kp1 = None
            self.p_max = None
            
            self.txop_factor = None
            self.backoff_kullback_leibler_divergence = None
            self.dist_factor = None
            self.aggressiveness_factor = None
            self.sifs_factor = None
            self.norm_factor = None
            self.geometric_factor = None

            self.last_iq_file = None
        
        def to_string(self):
            results = dedent("""\
                Found {} packets

                {} TXOPs
                min/mean/max Txop: {:.3f}µs {:.3f}µs {:.3f}µs
                Txop exceeding Txop limit: {}
                Txop factor: {:.3f}

                {} Backoffs
                min/mean/max Backoff: {:.3f}µs {:.3f}µs {:.3f}µs
                Backoff exceeding CW: {}
                Backoff Kullback-Leibler Divergence: {:.3f}
                Backoff KL Factor: {:.3f}

                Aggressiveness Factor: {:.3f}
                SIFS Factor: {:.3f}
                Norm Factor: {:.3f}
                Geometric Factor: {:.3f}
                """.format(self.number_of_packets,
                self.txop_stats.count,
                self.txop_stats.min, self.txop_stats.mean, self.txop_stats.max,
                self.txop_stats.violations,
                self.txop_factor,
                self.txop_stats.count,
                self.backoff_stats.min, self.backoff_stats.mean, self.backoff_stats.max,
                self.backoff_stats.violations,
                self.backoff_kullback_leibler_divergence,
                self.dist_factor,
                self.aggressiveness_factor,
                self.sifs_factor,
                self.norm_factor,
                self.geometric_factor))
            if any(self.backoff_bin_probabilities > self.p_max):
                results = results + "Backoff bin probability violation.\n"
            else:
                results = results + "Backoff bin probability compliant.\n"
            if any(self.txop_durations > self.txop_limit*1e3):
                results = results + "Txop duration violation.\n"
            else:
                results = results + "Txop duration compliant.\n"        
        
            norm_factor_percent = (1 - self.norm_factor)*100
            if self.aggressiveness_factor > 0:
                aggression = abs(self.aggressiveness_factor)*100
                results = results + "{:.3f}% aggressive / {:.3f}% compliant".format(aggression, norm_factor_percent)
            else:
                submission = abs(self.aggressiveness_factor)*100
                results = results + "{:.3f}% submissive / {:.3f}% compliant".format(submission, norm_factor_percent)
            
            return results
        
        def plot(self, path):
            plt.figure(1)
            plt.xlim((0,250))
            plt.hist(self.interframe_spacing, bins=750)
            plt.title("Histogram of the inter-frame spacing")
            plt.xlabel("Inter-frame spacing (microsecond)")
            plt.ylabel("Frequency")
            plt.draw()
            plt.savefig(os.path.join(path, 'interframe_spacing_histogram_{}.svg'.format(self.access_category)))
            plt.close()
        
            plt.figure(2)
            compliant_txop_durations = self.txop_durations[self.txop_durations < self.txop_limit*1e3]
            violating_txop_durations = self.txop_durations[self.txop_durations >= self.txop_limit*1e3]
            plt.hist(compliant_txop_durations, bins=50)
            plt.hist(violating_txop_durations, bins=50, color='red')
            plt.title("Histogram of the Txop durations")
            plt.xlabel("Txop duration (milli second)")
            plt.ylabel("Frequency")
            Gender = ['Compliant Txop', 'Violating Txop']
            plt.legend(Gender, loc=2)
            plt.draw()
            plt.savefig(os.path.join(path, 'txop_durations_histogram_{}.svg'.format(self.access_category)))
            plt.close()

            plt.figure(3)
            t = np.linspace(0, self.kp1-1, num=self.kp1)
            plt.bar(t, self.backoff_bin_probabilities, color='b', width=0.25)
            plt.bar(t+0.25, self.p_max, color='r', width=0.25)
            plt.title("Bin Probability and Threshold")
            plt.xlabel("Bin")
            plt.ylabel("Probability")
            Gender = ['Bin Probability', 'Compliance Upper threshold']
            plt.legend(Gender, loc=2)
            plt.draw()
            plt.savefig(os.path.join(path, 'bin_probability_{}.svg'.format(self.access_category)))
            plt.close()

            self.last_iq_file.plot(start = 0, num_samples = 100000, filename = os.path.join(path, "signal_magnitude_plot_{}.svg".format(self.access_category)))
            
    def __init__(self, uut_type, sample_rate = 20e6):
        self.uut_type = uut_type
        self.sample_rate = sample_rate
        self.access_category = None

        self.packet_duration = None
        self.interframe_spacing = None

        self.sifs = 25

    def loadIqSamples(self, iq_samples_file_name, noise_threshold=0.02):
        iqFile = IQSamplesFile(iq_samples_file_name, sample_rate=self.sample_rate, noise_threshold=noise_threshold)
        if self.access_category is not None:
            if self.access_category != iqFile.access_category:
                raise Exception("ERROR: Cannot mix samples from different access categories")
        else:
            self.set_access_category(iqFile.access_category)
        
        # calculate the interframe spacing by finding the time difference between the end and the start of each consecutive packets (in microseconds)
        interframe_spacing = (1e6/self.sample_rate)*(iqFile.packet_start_indices[1:]-iqFile.packet_end_indices[0:-1])
        packet_duration = (1e6/self.sample_rate)*(iqFile.packet_end_indices-iqFile.packet_start_indices)

        print("Found {} packets with {} IFSs in between".format(len(packet_duration), len(interframe_spacing)))
        if self.packet_duration is not None:
            self.packet_duration = np.concatenate([self.packet_duration, packet_duration])
            self.interframe_spacing = np.concatenate([self.interframe_spacing, [2 * self.sifs], interframe_spacing])
        else:
            self.packet_duration = packet_duration
            self.interframe_spacing = interframe_spacing

        self.last_iq_file = iqFile

    def get_results(self):        
        if self.packet_duration is None:
            print ("ERROR: No iq samples to analyze.")
            return

        results = ANTS_Analyzer.Results()
        results.interframe_spacing = self.interframe_spacing
        results.last_iq_file = self.last_iq_file
        
        number_of_packets = len(self.packet_duration)
        interframe_spacing_length = len(self.interframe_spacing)
        if number_of_packets != interframe_spacing_length + 1:
            print("ERROR: Expected one more packets than interframe spaces, but got {} / {}".format(number_of_packets, interframe_spacing_length))
            return
        results.number_of_packets = number_of_packets

        COT = np.where(self.interframe_spacing > self.sifs)
        COT = np.asarray(COT).T

        print("Analyzing {} packets, {} IFSs, {} COTs".format(number_of_packets, interframe_spacing_length, len(COT)))

        max_packet_duration = max(self.packet_duration)
        print("Max packet duration: {:.3f}µs".format(max_packet_duration))
        txop_durations = []
        # leave out last COT, it might be incomplete
        for i in range(0, len(COT)-1):
            txop_duration = 0
            start = COT[i][0]
            end = COT[i+1][0]
            # add packet durations during this COP - 
            for j in range(start + 1, end + 1):
                txop_duration = txop_duration + self.packet_duration[j]
            for j in range(start + 1, end):
                txop_duration = txop_duration + self.interframe_spacing[j]
            txop_durations.append(txop_duration)
        txop_durations = np.array(txop_durations)
        results.txop_durations = txop_durations

        mean_txop = np.mean(txop_durations)
        max_txop = np.max(txop_durations)
        min_txop = np.min(txop_durations)
        print("TXOP Min/Mean/Max: {:.3f}µs / {:.3f}µs / {:.3f}µs".format(min_txop, mean_txop, max_txop))
        
        if self.txop_limit == 0:
            # no txop limit, no violations
        	violating_durations = 0
        else:
        	violating_durations = np.count_nonzero(txop_durations > self.txop_limit * 1e3)

        results.txop_stats = ANTS_Analyzer.Stats(len(txop_durations), min_txop, mean_txop, max_txop, violating_durations)
        txop_factor = violating_durations/len(txop_durations)
        print("Found {:d} violating durations (> {:d}ms)".format(violating_durations, self.txop_limit))

        if self.uut_type == "Supervising" and (self.access_category == "voice" or self.access_category == "video") :
            correct_back_off = np.concatenate(np.where(self.interframe_spacing > self.sifs))
        else:
            # why +2???
            correct_back_off = np.concatenate(np.where(self.interframe_spacing > (self.sifs + 2)))
        
        slot_time = 9
        BFmin = self.aifs - slot_time/2
        BFmax = self.aifs + slot_time*(self.n-1) + slot_time/2
        BFmid = (BFmax + BFmin)/2

        back_offs = self.interframe_spacing[correct_back_off]
        results.backoff_stats = ANTS_Analyzer.Stats(len(back_offs), np.min(back_offs), np.mean(back_offs), np.max(back_offs), np.count_nonzero(back_offs > BFmax))
        blen = len(back_offs)
        b = np.asarray(np.zeros(self.n))
        b2 = np.asarray(np.zeros(self.kp1))

        for i in range(0, blen):
        	x = back_offs[i]
        	if x <= BFmin:
        		b[0] = b[0] + 1
        	elif x >= BFmax:
        		b[self.n-1] = b[self.n-1] + 1
        	else:
        		index = math.ceil((x-BFmin)/slot_time)-1
        		b[index] = b[index] + 1

        	if x < self.mind:
        		b2[0] = b2[0] + 1
        	elif x >= self.maxd:
        		b2[self.kp1-1] = b2[self.kp1-1] + 1
        	else:
        		index = math.ceil((x-self.mind)/slot_time)
        		b2[index] = b2[index] + 1

        prob = b/sum(b)
        nz_prob = prob[np.where(prob > 0)]
        backoff_kullback_leibler_divergence = sum(np.multiply(nz_prob, np.log10(nz_prob/(1/self.n))))
        dist_factor = 1 - np.exp(-1 * backoff_kullback_leibler_divergence)
        kk = np.arange((self.n - 1)/2, - (self.n - 1)/2-1, -1)
        accum = sum(np.multiply(b, kk))
        avrg = accum / blen
        mid = (self.n-1)/2
        aggressiveness_factor = avrg/mid
        SIFSs = self.interframe_spacing[np.where(self.interframe_spacing < 16 + 9/2)]
        SIFSs = SIFSs[np.where(SIFSs > 4)]
        sifs_factor = (np.mean(SIFSs) - 16)/16

        # Norm Factor
        norm_factor = math.sqrt(aggressiveness_factor**2 + txop_factor**2 + dist_factor**2 + sifs_factor**2)/2
        
        # Geometric mean Factor
        geometric_factor = ((1 - abs(aggressiveness_factor)) * (1 - txop_factor) * (1 - dist_factor) * (1 - abs(sifs_factor)))**(1/4)

        # Calculate the observed cumulative probabilities (p)
        e = blen  # total observed periods
        p = np.asarray(np.zeros(self.kp1))
        for i in range(0, self.kp1):
            p[i] = ANTS_Analyzer.sum_range(b2, 0, i)/e

        results.backoff_bin_probabilities = p    
        results.access_category = self.access_category
        results.txop_limit = self.txop_limit
        results.kp1 = self.kp1
        results.p_max = self.p_max
        results.txop_factor = txop_factor
        results.backoff_kullback_leibler_divergence = backoff_kullback_leibler_divergence
        results.dist_factor = dist_factor
        results.aggressiveness_factor = aggressiveness_factor
        results.sifs_factor = sifs_factor
        results.norm_factor = norm_factor
        results.geometric_factor = geometric_factor

        return results

    def sum_range(l,a,b):
        sum = 0
        for i in range(a, b+1,1):
            sum += l[i]
        return sum

    def set_access_category(self, access_category):
        """Sets the parameters that depend on the access category"""
        if access_category == "video":
            self.txop_limit = 4
            self.aifs = 34
            self.n = 8
            self.kp1 = 9
            self.mind = 32
            self.maxd = 95
        elif access_category == "best_effort":
        	self.txop_limit = 6
        	self.aifs = 43
        	self.n = 16
        	self.kp1 = 17
        	self.mind = 41
        	self.maxd = 176
        elif access_category == "background":
        	self.txop_limit = 6
        	self.aifs = 79
        	self.n = 16
        	self.kp1 = 17
        	self.mind = 77
        	self.maxd = 212
        elif access_category == "voice":
        	self.txop_limit = 2
        	self.aifs = 34
        	self.n = 4
        	self.kp1 = 5
        	self.mind = 32
        	self.maxd = 59
        else:
            raise Exception("Unknown access category {}".format(access_category))
        self.access_category = access_category

        self.p_max = np.asarray(np.zeros(self.kp1))
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
            raise Exception("Unknown access category {}".format(access_category))
        print("Running analysis for access category {}".format(self.access_category))

def main():
    if len(sys.argv) < 2:
        fileName = './tests/iqsamples_voice_run1.bin'
        print("Please supply the name of the .bin file")
    else:
        fileName = sys.argv[1]

    print("Analyzing {}...".format(fileName))
    analyzer = ANTS_Analyzer("Supervising")
    analyzer.loadIqSamples(fileName)
    results = analyzer.get_results()
    print("--- RESULTS ---")
    print(results.to_string())

    results.plot('.')

if __name__ == "__main__":
    main()        
