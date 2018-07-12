function packetLocationIndicate(fileName, f, mode, Duration)
close all;
duration = Duration; % in seconds
sampRate = 20e6;
[locs, threshold] = detectPacketLocations(fileName, sampRate, duration, f);

fid = fopen(fileName , 'r');
rawData = fread(fid, 2 * sampRate * duration, 'float32');
iData = rawData(1:2:end);
qData = rawData(2:2:end);
cData = iData + 1j * qData;

figure(3)
t = (0:(length(cData)-1))/sampRate;
indicator = zeros(size(t));
if mode == 1
    indicator(round(mean(locs, 2))) = 0.5 * max(abs(cData(:)));
elseif mode == 2
    indicator(locs(:)) = 0.5 * max(abs(cData(:)));
end
plot(t, abs(cData), 'b-',  t, sqrt(threshold) * ones(size(cData)), 'g--', t, indicator, 'r-');
legend('IQ', 'Thrshold')