function [locs, interference] = detectPacketLocationsV2(fileName, sampRate, duration)
% locs = detectPacketLocations(fileName, sampRate, duartion)
% Reads wifi data from the file fileName, and returns the start
% each packet.

fid = fopen(fileName , 'r');
rawData = fread(fid, 2 * sampRate * duration, 'float32');
iData = rawData(1:2:end);
qData = rawData(2:2:end);
cData = iData + 1j * qData;
envData = abs(cData).^2;

threshold = mean(envData) + sqrt(var(envData));
windowSize = 2e-6 * sampRate; % May change later
packetIndices = find(envData > threshold);
tempVector = diff(packetIndices);

packetStartIndices = packetIndices([true; tempVector> windowSize]);

locs = [packetStartIndices packetEndIndices];