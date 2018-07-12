clear; clc; close all;

fileName = 'Routers_1502_100M.bin';
sampRate = 20e6;
duration = 1;       % In seconds
packetIndex = 3;
f = 0.5;
% Find packetstart and end epochs
[locs, threshold] = detectPacketLocations(fileName, sampRate, duration, f);
%symDurations = (locs(:, 2) - locs(:, 1))/sampRate * 1e6;

%packetInd = find(symDurations > 60);

% Fetch the first packet
fid = fopen(fileName , 'r');
rawData = fread(fid, 2 * sampRate * duration, 'float32');
iData = rawData(1:2:end);       
qData = rawData(2:2:end);
cData = iData + 1j * qData;


%firstPacket = cData(locs(packetIndex, 1):locs(packetIndex, 2));
%figure
%plot((locs(packetIndex, 1):locs(packetIndex, 2))/sampRate, abs(firstPacket).^2)
%hold on
%plot((locs(packetIndex, 1):locs(packetIndex, 2))/sampRate, threshold * ones(size(firstPacket)), 'r--')
%[format, payLoad1, MACAggregation] = packetDecode(firstPacket, 20, sampRate);
%payLoad1(1:16)'
%[locs(packetIndex, 1), locs(packetIndex,2 )]/sampRate
durations = (locs(2:end, 1) - locs(1:(end-1),2))/20;
figure
hist(durations, 100)