function packetLocationIndicate_d(fileName, f, Start, End)
close all;
duration = inf; % in seconds
sampRate = 20e6;

fid = fopen(fileName , 'r');
rawData = fread(fid, 2 * sampRate * duration, 'float32');
iData = rawData(1:2:end);
qData = rawData(2:2:end);
cData = iData + 1j * qData;

cData(End + 1:end) = [];
cData(1:Start - 1) = [];

envData = abs(cData).^2;

threshold = f * mean(envData);
windowSize = 4e-6 * sampRate; % May change later
packetIndices = find(envData > threshold);
tempVector = diff(packetIndices);

packetEndIndices = packetIndices([tempVector > windowSize; true]);
packetStartIndices = packetIndices([true; tempVector> windowSize]);
locs = [packetStartIndices packetEndIndices];

figure(50)
t = (0:(length(cData)-1))/sampRate;
indicator = zeros(size(t));
indicator(locs(:)) = 0.5 * max(abs(cData(:)));
plot(t, abs(cData), 'b-',  t, sqrt(threshold) * ones(size(cData)), 'g--', t, indicator, 'r-');
legend('IQ', 'Thrshold')