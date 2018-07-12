close all; clear all;
fileName = 'AP11_to_AsusUsb42_QoS_0xVo_100M_n01.bin';
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

% mapObj = containers.Map('KeyType','double','ValueType','int64');
info = zeros(1, 3);

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

%             [info] = decomposeAMPDU(logical(payLoad), ii-1, info);
%             [MPDUinfo] = decomposeAMPDU(payLoad);
            
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
Load_and_Eval