import math
import numpy as np


def detect_packet_locations(file_name, samp_rate, f):
    # locs = detectPacketLocations(fileName, sampRate, duartion)
    # Reads wifi data from the file fileName, and returns the start and end location of
    # each packet.
    # Edit: Add check if fileName is not string and duration is not a number
    packet_start_indices = []
    packet_end_indices = []
    fid = open(file_name, "r")
    raw_data = np.fromfile(fid, dtype='<f4')
    fid.close()
    i_data = raw_data[0::2]
    q_data = raw_data[1::2]
    idl = len(i_data)
    qdl = len(q_data)
    if idl > qdl:
        i_data = i_data[0: qdl - 1]
    elif qdl > idl:
        q_data = q_data[0: idl - 1]
    c_data = i_data + 1j * q_data
    env_data = abs(c_data) ** 2
    threshold = f * np.mean(env_data)
    window_size = int(4e-6 * samp_rate)
    packet_indices = np.where(env_data > threshold)
    packet_indices = np.asarray(packet_indices)
    # packet_indices = packet_indices.T
    # print(packet_indices)
    temp_vector = np.diff(packet_indices).T
    packet_start_indices.append(packet_indices[0, 0])
    for i in range(0, len(temp_vector)):
        if temp_vector[i] > window_size:
            packet_end_indices.append(packet_indices[0, i])
            packet_start_indices.append(packet_indices[0, i+1])
    packet_end_indices.append(packet_indices[0, len(temp_vector)])
    locs = np.vstack((packet_start_indices, packet_end_indices)).T
    return locs, threshold


file_name = "0.bin"
duration = math.inf
samp_rate = 20e6
(locs, threshold) = detect_packet_locations(file_name, samp_rate,  0.02)
print(locs)
print(threshold)


