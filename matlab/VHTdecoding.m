
function [FrameBody] = VHTdecoding(IQPacketDataOffsetCorrection, foffset, fieldIndices, configObj, LSIGBITS, chEST)

rx = IQPacketDataOffsetCorrection;
pktOffset = foffset;
chEstLLTF = chEST;
chanBW = configObj.ChannelBandwidth;
rxLSIGBits = LSIGBITS;
%% Recover L-SIG field bits
% disp('Decoding L-SIG ... ');
% [rxLSIGBits, failCheck, eqLSIGSym] = wlanLSIGRecover(rx(pktOffset + (idxLSIG(1):idxLSIG(2)), :), ...
%     chanEstLLTF, noiseVarNonHT, chanBW);
%
% if failCheck % Skip L-STF length of samples and continue searching
%     disp('** L-SIG check fail **');
% else
%     disp('L-SIG check pass');
% end
%
% % Measure EVM of L-SIG symbol
% EVM = comm.EVM;
% EVM.ReferenceSignalSource = 'Estimated from reference constellation';
% EVM.ReferenceConstellation = helperReferenceSymbols('BPSK');
% rmsEVM = EVM(eqLSIGSym);
% fprintf('L-SIG EVM: %2.2f%% RMS\n', rmsEVM);
%
% % Calculate the receive time and corresponding number of samples in the
% % packet
% lengthBits = rxLSIGBits(6:17).';
% RXTime = ceil((bi2de(double(lengthBits)) + 3)/3) * 4 + 20; % us
% numRxSamples = RXTime * 1e-6 * sr; % Number of samples in receive time
%
% fprintf('RXTIME: %dus\n', RXTime);
% fprintf('Number of samples in packet: %d\n\n', numRxSamples);


rxLSIG = IQPacketDataOffsetCorrection(fieldIndices.LSIG(1):fieldIndices.LSIG(2));
LSIGBITS = wlanLSIGRecover(rxLSIG, chEST, 0.01, configObj.ChannelBandwidth);

% Check if valid format is received
if(isequal(LSIGBITS(19:24), zeros(6, 1)) && mod(sum(LSIGBITS(1:17)),2) == LSIGBITS(18))
    disp('LSIG check passed.')
else
    disp('LSIG check failed.')
end

%% Recover VHT-SIG-A field bits
disp('Decoding VHT-SIG-A... ');
rxVHTSIGA = IQPacketDataOffsetCorrection(fieldIndices.VHTSIGA(1):fieldIndices.VHTSIGA(2));
%[rxSIGABits, failCRC, eqSIGASym] = wlanVHTSIGARecover(rxVHTSIGA,chEstLLTF, noiseVarNonHT, chanBW);
[rxSIGABits, failCRC, eqSIGASym] = wlanVHTSIGARecover(rxVHTSIGA,chEstLLTF, 0.01, chanBW);


if failCRC
    disp('** VHT-SIG-A CRC fail **');
else
    disp('VHT-SIG-A CRC pass');
end

% Measure EVM of VHT-SIG-A symbols, first BPSK, second QBPSK
% release(EVM);
% EVM.ReferenceConstellation = helperReferenceSymbols('BPSK');
% rmsEVMSym1 = EVM(eqSIGASym(:,1));
% release(EVM);
% EVM.ReferenceConstellation = helperReferenceSymbols('QBPSK');
% rmsEVMSym2 = EVM(eqSIGASym(:,2));
% fprintf('VHT-SIG-A EVM: %2.2f%% RMS\n', mean([rmsEVMSym1 rmsEVMSym2]));

%% Create a VHT format configuration object by retrieving packet parameters
% from the decoded L-SIG and VHT-SIG-A bits
cfgVHTRx = helperVHTConfigRecover(rxLSIGBits, rxSIGABits);

% Display the transmission configuration obtained from VHT-SIG-A
vhtSigRecDisplaySIGAInfo(cfgVHTRx);

%% Obtain starting and ending indices for VHT-LTF and VHT-Data fields
% using retrieved packet parameters
idxVHTLTF  = wlanFieldIndices(cfgVHTRx, 'VHT-LTF');
idxVHTSIGB = wlanFieldIndices(cfgVHTRx, 'VHT-SIG-B');
idxVHTData = wlanFieldIndices(cfgVHTRx, 'VHT-Data');

% Warn if waveform does not contain whole packet
% if (pktOffset + double(idxVHTData(2))) > rxWaveLen
%     fprintf('** Not enough samples to recover entire packet **\n\n');
% end

%% Estimate MIMO channel using VHT-LTF and retrieved packet parameters
rxVHTLTF = IQPacketDataOffsetCorrection(fieldIndices.VHTLTF(1):fieldIndices.VHTLTF(2));
demodVHTLTF = wlanVHTLTFDemodulate(rxVHTLTF, cfgVHTRx);
chanEstVHTLTF = wlanVHTLTFChannelEstimate(demodVHTLTF, cfgVHTRx);

% Estimate noise power in VHT fields
noiseVarVHT = helperNoiseEstimate(demodLLTF, chanBW, cfgVHTRx.NumSpaceTimeStreams);

%% VHT-SIG-B Recover
disp('Decoding VHT-SIG-B...');
rxSIGB = IQPacketDataOffsetCorrection(fieldIndices.VHTSIGB(1):fieldIndices.VHTSIG(2));
[rxSIGBBits, eqSIGBSym] = wlanVHTSIGBRecover(rxSIGB, chanEstVHTLTF, noiseVarVHT, chanBW);

% Measure EVM of VHT-SIG-B symbol
% release(EVM);
% EVM.ReferenceConstellation = helperReferenceSymbols('BPSK');
% rmsEVM = EVM(eqSIGBSym);
% fprintf('VHT-SIG-B EVM: %2.2f%% RMS\n', rmsEVM);

% Interpret VHT-SIG-B bits to recover the APEP length (rounded up to a
% multiple of four bytes) and generate reference CRC bits
[refSIGBCRC, sigbAPEPLength] = helperInterpretSIGB(rxSIGBBits, chanBW, true);
disp('Decoded VHT-SIG-B contents: ');
fprintf('  APEP Length (rounded up to 4 byte multiple): %d bytes\n\n', sigbAPEPLength);

%% Recover PSDU bits using retrieved packet parameters and channel
% estimates from VHT-LTF
disp('Decoding VHT Data field...');
rxPSDU1 = IQPacketDataOffsetCorrection(fieldIndices.VHTData(1):fieldIndices.VHTData(2));
[rxPSDU, rxSIGBCRC, eqDataSym] = wlanVHTDataRecover( rxPSDU1, chanEstVHTLTF, noiseVarVHT, cfgVHTRx);

% Plot equalized constellation for each spatial stream
% refConst = helperReferenceSymbols(cfgVHTRx);
% [Nsd, Nsym, Nss] = size(eqDataSym);
% eqDataSymPerSS = reshape(eqDataSym, Nsd*Nsym, Nss);
% for iss = 1:Nss
%     constellationDiagram{iss}.ReferenceConstellation = refConst;
%     constellationDiagram{iss}(eqDataSymPerSS(:, iss));
% end

% Measure EVM of VHT-Data symbols
% release(EVM);
% EVM.ReferenceConstellation = refConst;
% rmsEVM = EVM(eqDataSym(:));
% fprintf('VHT-Data EVM: %2.2f%% RMS\n', rmsEVM);

%% Determine if any bits are in error, i.e. a packet error
packetError = any(biterr(txPSDU,rxPSDU));


% % 2 Byte � Frame Control
% % 2 Byte � Duration/ID
% % 4�6 Byte � Address 1 � 4
% % 2 Byte � Sequence Control
% % 2 Byte � QoS control
% % 4 Byte � HT Control (only for 802.11n frame

FrameControl = rxPSDU(1:2*8);
DuarationID = rxPSDU(2*8+1:4*8);
Address1 = rxPSDU(4*8+1:10*8);
Address2 = rxPSDU(10*8+1:16*8);
Address3 = rxPSDU(16*8+1:22*8);
SequenceControl = rxPSDU(22*8+1:24*8);
Address4 = rxPSDU(24*8+1:30*8);
QoScontrol = rxPSDU(30*8+1:34*8);
FrameBody = rxPSDU(44*8+1:end-4*8);
