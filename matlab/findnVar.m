close all; clear all;
fileName = 'Routers_1702_100M.bin';
sampRate = 20e6;
duration = 1;       % In seconds
packetIndex = 3;
f = 0.5;
% Find packetstart and end epochs
[locs, threshold] = detectPacketLocations(fileName, sampRate, duration, f);
%nVar = noiseVarEstimate(fileName, locs, duration, sampRate);
% Fetch the first packet
fid = fopen(fileName , 'r');
rawData = fread(fid, 2 * sampRate * duration, 'float32');
iData = rawData(1:2:end);
qData = rawData(2:2:end);
cData = iData + 1j * qData;
packet = cData(locs(3, 1):locs(3, 2));
nVar =  1e-3:1e-3:1;

for ii = 1:length(nVar)
    disp(ii)
    [~, payLoad1, MACAggregation] = packetDecode(packet, 20, sampRate, nVar(ii));
    payLoad = payLoad1(33:end);
    if(isequal(payLoad(1:2)',  zeros(1, 2)))
          if(isequal(payLoad(3:4)', [0 1]))
              getMAC(payLoad(32 + (1:48)))
              if(strcmp(getMAC(payLoad(32 + (1:48))),  '00:0D:67:71:B6:E9') || strcmp(getMAC(payLoad(32 + (1:48))),  '00:0D:67:71:A6:09'))
                keyboard;
              end
          end
    end
end