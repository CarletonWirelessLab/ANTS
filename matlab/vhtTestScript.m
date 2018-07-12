%%
% Set the parameters used throughout the example.
cbw = 'CBW20';                    % Channel bandwidth
fs = 20e6;                        % Sample rate (Hz)
ntx = 1;                           % Number of transmit antennas
nsts = 1;                          % Number of space-time streams
nrx = 1;                           % Number of receive antennas
%%
% Create a VHT configuration object that supports a 2x2 MIMO transmission
% and has an APEP length of 2000.
vht = wlanVHTConfig('ChannelBandwidth',cbw,'APEPLength', 2000, ...
    'NumTransmitAntennas',ntx,'NumSpaceTimeStreams',nsts, ...
    'SpatialMapping','Direct','STBC',false, 'ChannelCoding', 'LDPC', 'MCS', 0);
%%
% Generate a VHT waveform containing a random PSDU.
txPSDU = randi([0 1],vht.PSDULength*8,1);
txPPDU = wlanWaveformGenerator(txPSDU,vht);
%%
% Create a 2x2 TGac channel and an AWGN channel.
tgacChan = wlanTGacChannel('SampleRate',fs,'ChannelBandwidth',cbw, ...
    'NumTransmitAntennas',ntx,'NumReceiveAntennas',nrx, ...
    'LargeScaleFadingEffect','Pathloss and shadowing', ...
    'DelayProfile','Model-C');
awgnChan = comm.AWGNChannel('NoiseMethod','Variance', ...
    'VarianceSource','Input port');
%%
% Create a phase/frequency offset object.
pfOffset = comm.PhaseFrequencyOffset('SampleRate',fs,'FrequencyOffsetSource','Input port');
%%
% Calculate the noise variance for a receiver with a 9 dB noise figure.
% Pass the transmitted waveform through the noisy TGac channel.
nVar = 10^((-228.6 + 10*log10(290) + 10*log10(fs) + 9)/10) * 1e5;
%nVar = 1e-5;
rxPPDU = awgnChan(tgacChan(txPPDU), nVar);
% Introduce a frequency offset of 500 Hz.
rxPPDUcfo = pfOffset(rxPPDU,500);
[~, payLoad1, MACAggregation] = packetDecode(rxPPDUcfo, 20, fs , nVar);
numErr = biterr(txPSDU,payLoad1)
SNR = 10 * log10(mean(abs(rxPPDUcfo).^2)/nVar)