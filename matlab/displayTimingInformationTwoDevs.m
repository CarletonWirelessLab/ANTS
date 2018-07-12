clc;  close all; clear all;
fileName = 'TwoRALink_2202_50M_50M.bin';
sampRate = 20e6;
duration = inf;       % In seconds
packetIndex = 3;
f = 0.01;

Tx1Ad = '60:A4:4C:EC:73:42';  % ASUS USB HI power
% Tx2Ad = '14:CC:20:1F:25:C9';
Tx2Ad = '60:A4:4C:EC:73:0C';  % ASUS USB Low power

% Find packetstart and end epochs
[locs, threshold] = detectPacketLocations(fileName, sampRate, duration, f);
%symDurations = (locs(:, 2) - locs(:, 1))/sampRate * 1e6;
nVar = noiseVarEstimate(fileName, locs, duration, sampRate);
 
%packetInd = find(symDurations > 60);
IFS = (locs(2:end, 1) - locs(1:(end-1), 2))/sampRate * 1e6;
IFSI = zeros(size(IFS));  %6 = null data || 4, 5 = Data, b2bData || 1 = ACK, BA, || 2 = Beacon || 3 = BAR

% Read data
fid = fopen(fileName , 'r');
rawData = fread(fid, 2 * sampRate * duration, 'float32');
iData = rawData(1:2:end);
qData = rawData(2:2:end);
cData = iData + 1j * qData;

for ii = 2:(length(locs)-1)
    packet = cData(locs(ii, 1):locs(ii, 2));
    disp(['Packet #' char(string(ii)) ':'])
    try
        [frmt, payLoad1, MACAggregation] = packetDecode(packet, 20, sampRate, nVar);
    catch
        continue
    end
    if(MACAggregation)
        payLoad = payLoad1(33:end);
    else
        payLoad = payLoad1;
    end
    frameControlField = payLoad(1:16)';
    subTypeSeq = frameControlField(8:-1:5);
    if(isequal(frameControlField(1:2),  zeros(1, 2)))
        if(frameControlField(12))
%             keyboard;
        end
        if(isequal(frameControlField(3:4), zeros(1,2)))
            if(isequal(subTypeSeq, [1 0 0 0]))
                subtype = 'Beacon';
                IFSI(ii - 1) = 2;
            end
            
        elseif(isequal(frameControlField(3:4), [1 0]))           
            if(isequal(subTypeSeq, [1 0 0 0]))
                subtype = 'BAR';
                IFSI(ii - 1) = 3;
            elseif(isequal(subTypeSeq, [1 0 1 1]))
                  subtype = 'RTS';
                  IFSI(ii - 1) = 8;
            elseif(isequal(subTypeSeq, [1 1 0 0]))
                  subtype = 'CTS';
                  IFSI(ii - 1) = 8;
            elseif(isequal(subTypeSeq, [1 0 0 1]))
                subtype = 'BA';
                IFSI(ii - 1) = 1;
            elseif(isequal(subTypeSeq, [1 1 0 1]))
                subtype = 'ACK';
                IFSI(ii - 1) = 1;
            end
        elseif(isequal(frameControlField(3:4), [0 1]))
            type = 'data';
            TxMACAd = getMAC(payLoad(80 + (1:48)));
            if(isequal(subTypeSeq, [0 0 0 0]))
                subtype = 'Data';
                if(strcmp(TxMACAd, Tx1Ad))
                    IFSI(ii - 1) = 4;
                elseif(strcmp(TxMACAd, Tx2Ad))
                    IFSI(ii - 1) = 5;
                end
            elseif(isequal(subTypeSeq, [0 1 0 0]))
                subtype = 'Null data';
                IFSI(ii - 1) = 6;
            elseif(isequal(subTypeSeq, [1 0 0 0]))
                subtype = 'QOS data';
                if(strcmp(TxMACAd, Tx1Ad))
                    IFSI(ii - 1) = 4;
                elseif(strcmp(TxMACAd, Tx2Ad))
                    IFSI(ii - 1) = 5;
                end
            elseif(isequal(subTypeSeq, [1 1 0 0]))
                subtype = 'QOS Null';
                IFSI(ii - 1) = 6;
            end
        end
    end
end

unknownCount = sum(IFSI == 0);
unknownIDs = find(IFSI == 0) + 1;
unknownIFS = IFS(unknownIDs - 1);

ACKCount = sum(IFSI == 1);
ACKIDs = find(IFSI == 1) + 1;
ACKIFS = IFS(ACKIDs - 1);

BeaconsCount = sum(IFSI == 2);
BeaconsIDs = find(IFSI == 2) + 1;
BeaconsIFS = IFS(BeaconsIDs - 1);

BARCount = sum(IFSI == 3);
BARIDs = find(IFSI == 3) + 1;
BARIFS = IFS(BARIDs - 1);

DataCount1 = sum(IFSI == 4);
DataIDs1 = find(IFSI == 4) + 1;
DataIFS1 = IFS(DataIDs1 - 1);

DataCount2 = sum(IFSI == 5);
DataIDs2 = find(IFSI == 5) + 1;
DataIFS2 = IFS(DataIDs2 - 1);

nullDataCount = sum(IFSI == 6);
nullDataIDs = find(IFSI == 6) + 1;
nullDataIFS = IFS(nullDataIDs - 1);

clc;
disp(['- Found ', num2str(length(IFS)), ' packets']);
disp(['- Acks/BAs = ', num2str(ACKCount)]);
disp(['- BAR = ', num2str(BARCount)]);
disp(['- Beacons = ', num2str(BeaconsCount)]);
disp(['- Data (Tx1) = ', num2str(DataCount1)]);
disp(['- Data (Tx2) = ', num2str(DataCount2)]);
disp(['- Null Data = ', num2str(nullDataCount)]);
disp(['- Unknown = ', num2str(unknownCount)]);

SIFS = mean(IFS(IFSI == 1))

frameControlField = IFS(IFSI == 2);
PIFS = mean(frameControlField)

backOffTx1 = IFS(IFSI == 4);
meanDIFS1 = mean(backOffTx1)
minBackOff1 = min(backOffTx1)
figure(1)
hist(backOffTx1, 16)

backOffTx2 = IFS(IFSI == 5);
meanDIFS2 = mean(backOffTx2)
minBackOff2 = min(backOffTx2)
figure(2)
hist(backOffTx2, 16)
