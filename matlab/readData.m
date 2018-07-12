% Reads data.bin
% Performs PHY decoding
clc; clear; close all;
samp_rate = 20e6; % Always 20 MHz for now
seq_len = 1; % In seconds
fid = fopen('oneWayUDP/SETUP_2601.bin', 'r');
iq_data = fread(fid, 2 * seq_len * samp_rate, 'float32');
i_data = iq_data(1:2:end);
q_data = iq_data(2:2:end);
env_data = i_data.^2 + q_data.^2;
f = 1;

% Plot Packets
t = (0:(length(i_data)-1))/samp_rate;
figure
plot(t, env_data);

% Energy Detection to detect packets (Could be performed using built-in function)
threshold = f * (mean(env_data) + std(env_data)); window_size = 20;
packet_indices = find(env_data > threshold);
hold on
plot(t, threshold * ones(size(t)), 'r--')
legend('IQ power', 'Threshold')

temp_vector = diff(packet_indices);
packet_end_indices = packet_indices([temp_vector > window_size; false]);
first_packet = i_data(packet_indices(1):packet_end_indices(1)) + 1j * q_data(packet_indices(1):packet_end_indices(1));
t_first_packet = t(packet_indices(1):packet_end_indices(1));

figure
title('First Packet')
plot(t_first_packet, abs(first_packet).^2)

% Packet Processing
pfOffset = comm.PhaseFrequencyOffset('SampleRate',samp_rate,'FrequencyOffsetSource','Input port');
configObj = wlanHTConfig;
frame_indices = wlanFieldIndices(configObj);
rxLSTF = first_packet(frame_indices.LSTF(1):frame_indices.LSTF(2));
% 1) Coarse Frequency estimate
foffset = wlanCoarseCFOEstimate(rxLSTF, 'CBW20');
first_packet_offsetCorr = pfOffset(first_packet,-foffset);

% 2) Fine Frequency estimate
rxLLTF = first_packet_offsetCorr(frame_indices.LLTF(1):frame_indices.LLTF(2));
foffset = wlanFineCFOEstimate(rxLLTF,'CBW20');
first_packet_offsetCorr = pfOffset(first_packet_offsetCorr,-foffset);

% Channel estimation
rxLLTF = first_packet_offsetCorr(frame_indices.LLTF(1):frame_indices.LLTF(2));
demodSig = wlanLLTFDemodulate(rxLLTF,configObj);
chEst = wlanLLTFChannelEstimate(demodSig,'CBW20');

% Recover Legacy Signal Field
rxLSig = first_packet_offsetCorr(frame_indices.LSIG(1):frame_indices.LSIG(2));
LSIGBits = wlanLSIGRecover(rxLSig,chEst,0.01,'CBW20'); 

% Recover HT Signal Field
rxHTSIG = first_packet_offsetCorr(frame_indices.HTSIG(1):frame_indices.HTSIG(2));
[HTSIGBits, CRCbitFail] = wlanHTSIGRecover(rxHTSIG, chEst, 0.01, 'CBW20');