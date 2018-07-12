close all; clear all;
fileName = 'AP11_to_AsusUsb42_QoS_0xVi_100M.bin';
accessCategory = 0; % 0 = Voice, 1 = Video, 2 = Best Effort, 3 = BackGround

sampRate = 20e6;
duration = inf;       % In seconds
packetIndex = 3;
f = 0.01;

Asus42MAC     = '60:A4:4C:EC:73:42';  % ASUS USB HI power
Asus0CMAC     = '60:A4:4C:EC:73:0C';  % ASUS USB Low power
Ericsson_AP11 = '00:0D:67:71:B6:E9';  % Ericsson AP-6321 .11

deviceTxMAC = Ericsson_AP11;
deviceRxMAC = Asus42MAC;

% Find packetstart and end epochs
[locs, threshold] = detectPacketLocations(fileName, sampRate, duration,f);%Kareem's code
% [locs, threshold] = PacketDetection (fileName, sampRate, duration, f); % Salime's Code

%symDurations = (locs(:, 2) - locs(:, 1))/sampRate * 1e6;
nVar = noiseVarEstimate(fileName, locs, duration, sampRate);
 
%packetInd = find(symDurations > 60);
IFS = (locs(2:end, 1) - locs(1:(end-1), 2))/sampRate * 1e6;
IFSI = zeros(size(IFS));  %6 = null data || 4, 5 = Data, b2bData || 
% 1 = ACK, BA, || 2 = Beacon || 3 = BAR || 7 = RTS || 8 = CTS || 10 = % unwanted Data (different Tx or Rx)
 
% Read data
fid = fopen(fileName , 'r');
rawData = fread(fid, 2 * sampRate * duration, 'float32');
iData = rawData(1:2:end);
qData = rawData(2:2:end);
cData = iData + 1j * qData;

for ii = 3:(length(locs)-1)
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
        if(frameControlField(12)) % retry bit is 1
            %keyboard;
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
                IFSI(ii - 1) = 7;
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
            
            packetRxMAC = getMAC(payLoad(32 + (1:48)));
            packetTxMAC = getMAC(payLoad(80 + (1:48)));
            
            if (packetTxMAC == deviceTxMAC & packetRxMAC == deviceRxMAC)
                if(isequal(subTypeSeq, [0 0 0 0]))
                    subtype = 'Data';
                    if(IFSI(ii - 2) == 4 || IFSI(ii - 2) == 5)
                        IFSI(ii - 1) = 5;
                    else
                        IFSI(ii - 1) = 4;
                    end
                elseif(isequal(subTypeSeq, [0 1 0 0]))
                    subtype = 'Null data';
                    IFSI(ii - 1) = 6;
                elseif(isequal(subTypeSeq, [1 0 0 0]))
                    subtype = 'QOS data';
                    if(IFSI(ii - 2) == 4 || IFSI(ii - 2) == 5)
                        IFSI(ii - 1) = 5;
                    else
                        IFSI(ii - 1) = 4;
                    end
                elseif(isequal(subTypeSeq, [1 1 0 0]))
                    subtype = 'QOS Null';
                    IFSI(ii - 1) = 6;
                end
            else
                IFSI(ii - 1) = 10;  
            end
        end
    end
end
%% Save Output

save([fileName(1:end-4) '.mat'],'IFS','IFSI','locs','sampRate', 'accessCategory');

%%
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

DataCount = sum(IFSI == 4);
DataIDs = find(IFSI == 4) + 1;
DataIFS = IFS(DataIDs - 1);

b2bDataCount = sum(IFSI == 5);
b2bDataIDs = find(IFSI == 5) + 1;
b2bDataIFS = IFS(b2bDataIDs - 1);

nullDataCount = sum(IFSI == 6);
nullDataIDs = find(IFSI == 6) + 1;
nullDataIFS = IFS(nullDataIDs - 1);

RTSCount = sum(IFSI == 7);
RTSIDs = find(IFSI == 7) + 1;
RTSIFS = IFS(RTSIDs - 1);

CTSCount = sum(IFSI == 8);
CTSIDs = find(IFSI == 8) + 1;
CTSIFS = IFS(CTSIDs - 1);

unwantedDataCount = sum(IFSI == 10);
unwantedDataIDs = find(IFSI == 10) + 1;
unwantedDataIFS = IFS(unwantedDataIDs - 1);

    
AIFS = 0;
switch accessCategory
    case 0 % vioce
        AIFS = 34;
    case 1 % video
        AIFS = 34;
    case 2 % BestEffort
        AIFS = 43;
    case 3 % Background
        AIFS = 79;
end


% Calculate TXOP 
if RTSCount < DataCount
    PacketCount = DataCount;
    PacketIDs = DataIDs;
    PacketIFS = DataIFS;
else
    PacketCount = RTSCount;
    PacketIDs = RTSIDs;
    PacketIFS = RTSIFS;
end
TxopCount = 1;
TxopStartEnd = zeros(size(IFS,1),2);
for dindex = 1:PacketCount
    if PacketIFS(dindex) > 19  % end/beginig of a Txop
        
        TxopStartEnd(TxopCount,2) = locs(PacketIDs(dindex)-1,2); % end of previus txop
        TxopStartEnd(TxopCount + 1,1) = locs(PacketIDs(dindex),1); % start of next txop
        
        TxopCount = TxopCount + 1;
    end
end
TxopStartEnd(TxopCount,2) = locs(end,2);
TxopStartEnd(TxopCount+1:end,:) = [];
TxopDurations = (TxopStartEnd(:,2) - TxopStartEnd(:,1))/sampRate * 1e3;  %mSec;

%
disp('#####################################');
disp(['- Found ', num2str(length(IFS)), ' packets']);
disp(['- Acks/BAs = ', num2str(ACKCount)]);
disp(['- RTS/CTSs = ', num2str(RTSCount), '/' , num2str(CTSCount)]);
disp(['- BAR = ', num2str(BARCount)]);
disp(['- Beacons = ', num2str(BeaconsCount)]);
disp(['- Data (no back to back) = ', num2str(DataCount)]);
disp(['- Data (back to back) = ', num2str(b2bDataCount)]);
disp(['- Null Data = ', num2str(nullDataCount)]);
disp(['- Unknown = ', num2str(unknownCount)]);
disp(['- Unwanted Data = ', num2str(unwantedDataCount)]);

SIFS = mean(IFS(IFSI == 1))

frameControlField = IFS(IFSI == 2);
PIFS = mean(frameControlField)

if RTSCount < DataCount   % No RTS
    
    %%%% Slilance Periods
    backOff = IFS(IFSI == 4);
    minBackOff = min(backOff)
    gtitle = 'Histogram of Data Associated silent periods (X)';
    xlab = 'time (uSec)';
    histScales(2, backOff, 20, gtitle, xlab, 1, [0 max(ceil(max(backOff)), 150)]);
    
    %%%%% n
    CorrectBackOff = backOff(backOff > 27); % 27 uSec, Guido's recommendation
    minCorrectBackOff = min(CorrectBackOff)
    n = (CorrectBackOff - AIFS)/9;
    gtitle = 'n BackOffs Histogram';
    xlab = 'n';
    histScales(3, n, 20, gtitle, xlab, 1, [-1 16]);

else % RTS exists
    
    %%%% Slilance Periods
    DIFSofRTS = IFS(IFSI == 7);
    meanDIFSofRTS = mean(DIFSofRTS);
    minDIFSofRTS = min(DIFSofRTS)

    gtitle = 'Histogram of RTS Associated silent periods (X)';
    xlab = 'time (uSec)';
    histScales(5, DIFSofRTS, 20, gtitle, xlab, 1, [0 ceil(max(DIFSofRTS))]);
    
    %  n
    n = (DIFSofRTS - AIFS)/9;
    gtitle = 'n BackOffs Histogram RTS';
    xlab = 'n';
    histScales(6, n, 20, gtitle, xlab, 1, [-1 16]);
    
end

%%%%  TXOP
meanTxop = mean(TxopDurations)
maxTxop = max(TxopDurations)

gtitle = 'TXOP duration Histogram';
xlab = 'time (uSec)';
histScales(4, TxopDurations, 20, gtitle, xlab, 0.05, [0 ceil(max(TxopDurations))]);
