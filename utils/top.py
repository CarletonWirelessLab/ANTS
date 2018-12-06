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

global name
global access_category
name = 'Ericsson'
access_category = "voice"
if len(sys.argv) > 1:
        name   = sys.argv[1]
        access_category = sys.argv[2]



file_name = name + '_' + access_category + '.bin'


sampling_rate = 20e6
if access_category == "voice":
	TxopLimit = 2
	AIFS = 34
	N = 4
	kp1 = 5
	mind = 32
	maxd = 59
elif access_category == "video":
	TxopLimit = 4
	AIFS = 34
	N = 8
	kp1 = 9
	mind = 32
	maxd = 95
elif access_category == "best_effort":
	TxopLimit = 6
	AIFS = 43
	N = 16
	kp1 = 17
	mind = 41
	maxd = 176
elif access_category == "background":
	TxopLimit = 6
	AIFS = 79
	N = 16
	kp1 = 17
	mind = 77
	maxd = 212
else:
	TxopLimit = 2
	AIFS = 34
	N = 4
	kp1 = 5
	mind = 32
	maxd = 59

# open and read the data from the binary file
with open(file_name, mode='rb') as file: # b is important -> binary
	data = np.fromfile(file, dtype=np.float32)
file.close()

# the data is divided into inphase and quadrature data
# inphase data are at the even indices, cos(wt)
file_length = len(data) #added
inphase_data = data[0:file_length:2]
# quadrature data are at the odd indices, sin(wt)
quadrature_data = data[1:file_length:2]

# delete data to free some space, inphase and quadrature have the needed data
del data
# find the common length of the inphase and quadrature data
data_length = min(len(inphase_data), len(quadrature_data))
duration = data_length/sampling_rate
# have both vectors to be of the same length, the length of the shorter vector
inphase_data = inphase_data[0:data_length]
quadrature_data = quadrature_data[0:data_length]
# set the time axis from the data length and the total duration
time = np.linspace(0, duration, num=data_length)
# combine inphase and quadrature components as a complex number, cos(wt) + 1j*sin(wt)
complex_data = inphase_data + (1j*quadrature_data)
del inphase_data
del quadrature_data
# find the power of the signal using the square of the magnitude of the complex data
power_data = abs(complex_data)**2
del complex_data
# set a minimum threshold value for noise
f = 0.02
threshold = f * np.mean(power_data)
# disregard the fluctuations of the signal in the packet
packet_indices = np.concatenate(np.where(power_data > threshold)) #added
temp_vector = np.diff(packet_indices) #added

# possible wait time between packets in seconds
wait_time = 4e-6
# number of samples from the start of the packet to safely assume that the packet is complete but before the arrival of the next packet
window_size = int(sampling_rate*wait_time)
temp_vector_length = len(temp_vector)
temp_indices = np.concatenate(np.where(temp_vector > window_size))

# an array to store the indices of the end of the packet
packet_end_indices = np.array([0]*(len(temp_indices)+1))
packet_end_indices[0:(len(temp_indices)):1] = packet_indices[temp_indices]
packet_end_indices[len(temp_indices)] = packet_indices[-1]

# an array to store the indices of the start of the packet
packet_start_indices = np.array([0]*(len(temp_indices)+1))
packet_start_indices[1:(len(temp_indices)+1):1] = packet_indices[temp_indices+1]
packet_start_indices[0] = packet_indices[0]

# free some space
del packet_indices
# calculate the number of packets received
number_of_packets = len(packet_start_indices)
# sort the indices of the end of the packet in an ascending order

i = 0
packet_indicator = np.zeros([data_length, 1])
packet_indicator[packet_start_indices] = 1
packet_indicator[packet_end_indices] = 1



# calculate the interframe spacing by finding the time difference between the end and the start of each consecutive packets (in microseconds)
interframe_spacing = (1e6/sampling_rate)*(packet_start_indices[1:]-packet_end_indices[0:-1])
packet_duration = (1e6/sampling_rate)*(packet_end_indices-packet_start_indices)

interframe_spacing_length = len(interframe_spacing)
COT = np.where(interframe_spacing > 25)
COT = np.asarray(COT).T

packet_indices = np.concatenate(np.where(power_data > threshold)) #added
SIFSD = np.concatenate(np.where(interframe_spacing <= 20.5))
correct_back_off = np.concatenate(np.where(interframe_spacing > 27))
Txop_durations = []
COT_length = len(COT)
i = 1
while i < COT_length:
	a = (1e3 / sampling_rate) * (packet_end_indices[COT[i]] - packet_start_indices[COT[i - 1] + 1])
	if a != 0:
		Txop_durations.append(a)
	i = i + 1
Txop_durations = np.concatenate(Txop_durations)

min_back_off = min(interframe_spacing)
mean_txop = np.mean(Txop_durations)
max_txop = np.max(Txop_durations)

PacketsDurations = (1e6 / sampling_rate) * (packet_end_indices - packet_start_indices)
maxPacketDuration = max(PacketsDurations)/1e3



if TxopLimit == 0:
	violatingDurations = Txop_durations[np.concatenate(np.where(Txop_durations > maxPacketDuration))]
else:
	violatingDurations = Txop_durations[np.concatenate(np.where(Txop_durations > TxopLimit))]
TxopFactor = (len(violatingDurations)/len(Txop_durations))


slotTime = 9
BFmin = AIFS - slotTime/2
BFmax = AIFS + slotTime*(N-1) + slotTime/2
BFmid = (BFmax + BFmin)/2

BackOffs = interframe_spacing[correct_back_off]
blen = len(BackOffs)
B = np.asarray(np.zeros(N))
B2 = np.asarray(np.zeros(kp1))
for i in range(0, blen):
	x = BackOffs[i]
	if x <= BFmin:
		B[0] = B[0] + 1
	elif x >= BFmax:
		B[N-1] = B[N-1] + 1
	else:
		index = math.ceil((x-BFmin)/slotTime)-1
		B[index] = B[index] + 1

	if x < mind:
		B2[0] = B2[0] + 1
	elif x >= maxd:
		B2[kp1-1] = B2[kp1-1] + 1
	else:
		index = math.ceil((x-mind)/slotTime)
		B2[index] = B2[index] + 1
prob = B/sum(B)
nzProb = prob[np.where(prob > 0)]
KBL = -sum(np.multiply(nzProb, np.log10(nzProb/(1/N))))
DistFactor = 1 - np.exp(KBL)
KK = numpy.arange((N - 1)/2, -(N - 1)/2-1, -1)
accum = sum(np.multiply(B, KK))
avrg = accum / blen
mid = (N-1)/2
AGFactor = avrg/mid
SIFSs = interframe_spacing[np.where(interframe_spacing < 16 + 9/2)]
SIFSs = SIFSs[np.where(SIFSs > 4)]
SIFSFactor = (np.mean(SIFSs) - 16)/16

# Norm Factor
NF = math.sqrt(AGFactor**2 + TxopFactor**2 + DistFactor**2 + SIFSFactor**2)/2
NFP = (1 - NF)*100

# Geometric mean Factor
GF = ((1 - abs(AGFactor)) * (1 - TxopFactor) * (1 - DistFactor) * (1 - abs(SIFSFactor)))**(1/4)

# Calculate the observed cumulative probabilities (p)
E = blen  # total observed periods
p = np.asarray(np.zeros(kp1))
pMax = np.asarray(np.zeros(kp1))

def sum_range(l,a,b):
	sum = 0
	for i in range(a, b+1,1):
		sum += l[i]
	return sum


for i in range(0, kp1):
	p[i] = sum_range(B2, 0, i)/E
pMax[0] = 0.05
pMax[kp1-1] = 1

if access_category == "voice":
	for i in range(1, 4):
		pMax[i] = pMax[0] + i * 0.25
elif access_category == "video":
	pMax[1] = 0.18
	for i in range(2, 7):
		pMax[i] = pMax[1] + (i - 1) * 0.125
	pMax[kp1 - 2] = 1
elif access_category == "best_effort" or access_category == "background":
	pMax[1] = 0.12
	for i in range(2, 16):
		pMax[i] = pMax[1] + (i - 1) * 0.0625
else:
	for i in range(1, 4):
		pMax[i] = pMax[0] + i * 0.25




output_file = open(name+"_"+access_category+"_results.txt", "w")

#if (np.sum((p - pMax)/pMax > 0.001)==0): #sum(p > pMax)
#	print("Unit Complies with the Standard")
#	output_file.write("Unit Complies with the Standard"+"\n")
#else:
#	print("Unit does not Comply with the Standard")
#	output_file.write("Unit does not Comply with the Standard"+"\n")
#
#if sum(p > pMax): #
#	print("Unit does not Comply with the Standard")
#	output_file.write("Unit does not Comply with the Standard"+"\n")
#else:
#	print("Unit Complies with the Standard")
#	output_file.write("Unit Complies with the Standard"+"\n")
	


# print results
print("Found " + str(len(packet_end_indices)) + " packets, " + str(len(interframe_spacing)) + " IFSs")
print("minBackOff: " + str(min_back_off))
print("meanTxop: " + str(mean_txop))
print("maxTxop: " + str(max_txop))
print("TxopFactor: " + str(TxopFactor))
print("KBL: " + str(KBL))
print("DistFactor: " + str(DistFactor))
print("AGFactor: " + str(AGFactor))
print("SIFSFactor: " + str(SIFSFactor))
print("NF: " + str(NF))
print("GF: " + str(GF))
output_file.write("Found " + str(len(packet_end_indices)) + " packets, " + str(len(interframe_spacing)) + " IFSs"+"\n")
output_file.write("minBackOff: " + str(min_back_off)+"\n")
output_file.write("meanTxop: " + str(mean_txop)+"\n")
output_file.write("maxTxop: " + str(max_txop)+"\n")
output_file.write("TxopFactor: " + str(TxopFactor)+"\n")
output_file.write("KBL: " + str(KBL)+"\n")
output_file.write("DistFactor: " + str(DistFactor)+"\n")
output_file.write("AGFactor: " + str(AGFactor)+"\n")
output_file.write("SIFSFactor: " + str(SIFSFactor)+"\n")
output_file.write("NF: " + str(NF)+"\n")
output_file.write("GF: " + str(GF)+"\n")

if AGFactor > 0:
	print(str(abs(AGFactor)*100) + " Aggressive and " + str(NFP) + " Compliant")
	output_file.write(str(abs(AGFactor)*100) + " Aggressive and " + str(NFP) + " Compliant"+"\n")
else:
	print(str(abs(AGFactor) * 100) + " Submissive and " + str(NFP) + " Compliant")
	output_file.write(str(abs(AGFactor) * 100) + " Submissive and " + str(NFP) + " Compliant"+"\n")

	
# generate a plot for the power of the signal and the packet indicators
plt.figure(1)
plt.plot(time, np.sqrt(power_data), 'b-', time, packet_indicator, 'r-')#, time, packet_indicator, 'r-')
plt.title("Plot of the magnitude of the signal vs Time")
plt.xlabel("Time (sec)")
plt.ylabel("Signal magnitude") #find out if the power is in Watts or dB?
plt.draw()
plt.savefig(name+'_'+access_category+'_signal_magnitude_plot.png')

plt.figure(2)
plt.xlim((0,300))
plt.hist(interframe_spacing,bins=500)
plt.title("Histogram of the inter-frame spacing")
plt.xlabel("Inter-frame spacing (microsecond)")
plt.ylabel("Frequency")
plt.draw()
plt.savefig(name+'_'+access_category+'_interframe_spacing_histogram.png')

plt.figure(3)

plt.hist(Txop_durations,bins=100)
plt.title("Histogram of the Txop durations")
plt.xlabel("Txop duration (milli second)")
plt.ylabel("Frequency")
plt.draw()
plt.savefig(name+'_'+access_category+'_txop_durations_histogram.png')

plt.figure(4)
t = np.linspace(0, kp1-1, num=kp1)
plt.bar(t, p, color='b', width=0.25)
plt.bar(t+0.25, pMax, color='r', width=0.25)
plt.title("Bin Probability and Threshold")
plt.xlabel("Bin")
plt.ylabel("Probability")
Gender = ['Bin Probability', 'Compliance Upper threshold']
plt.legend(Gender, loc=2)
plt.draw()
plt.savefig(name+'_'+access_category+'_bin_probability.png')

plt.show(block=False)

output_file.close()

input("Hit enter to exit...")
# ask user to hit enter




