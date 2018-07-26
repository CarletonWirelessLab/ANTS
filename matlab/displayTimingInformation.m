% close all; clear all;
% fileName = 'FgTest_123.bin';
accessCategory = 2; % 0 = Voice, 1 = Video, 2 = Best Effort, 3 = BackGround
IntDuration = 0; % mSec

tic
sampRate = 20e6;
%duration = 2;       % In seconds
packetIndex = 3;
f = 0.01;

Asus42MAC     = '60:A4:4C:EC:73:42';  % ASUS USB HI power
Asus0CMAC     = '60:A4:4C:EC:73:0C';  % ASUS USB Low power
CiscoBAMAC    = '00:1E:E5:E2:D1:BA';  % Cisco USB adaptor
DLink55MAC    = '90:94:E4:0A:7D:55';  % D-Link USB adaptor

Ericsson_AP11 = '00:0D:67:71:B6:E9';  % Ericsson AP-6321 .11
AsusAP_B8     = '40:16:7E:F3:F2:BC';  % Asus AP BC
BelairAP_B8   = '00:0D:67:3F:5E:4E';  % BelAir AP E4

AcerLaptop    = '24:FD:52:96:E9:AC';  % Acer Laptop Aspir R7

deviceRxMAC = Asus42MAC;
deviceTxMAC = BelairAP_B8;

% Find packetstart and end epochs
[locs, threshold] = detectPacketLocations(fileName, sampRate, duration,f); %Kareem's code
% [locs] = PacketDetection (fileName, sampRate, duration, 20); % Salime's Code

%symDurations = (locs(:, 2) - locs(:, 1))/sampRate * 1e6;
nVar = noiseVarEstimate(fileName, locs, duration, sampRate);

%packetInd = find(symDurations > 60);
IFS = (locs(2:end, 1) - locs(1:(end-1), 2))/sampRate * 1e6;
IFSI = zeros(size(IFS));  %6 = null data || 4, 5 = Data, b2bData || 14 = Retransmission Data, b2bData
% 1 = ACK, BA, || 2 = Beacon || 3 = BAR || 7 = RTS || 8 = CTS || 10 = % unwanted Data (different Tx or Rx)

% Read data
fid = fopen(fileName , 'r');
rawData = fread(fid, 2 * sampRate * duration, 'float32');
iData = rawData(1:2:end);
qData = rawData(2:2:end);
cData = iData + 1j * qData;

% power = 10*log10(abs(cData(1:100000)).^2);
% plot(power)

% mapObj = containers.Map('KeyType','double','ValueType','int64');
info = zeros(1, 3);
disp('#########################')
for ii = 2:(length(locs))
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

                if payLoad(12)  % Data Retransmission
                        IFSI(ii - 1) = 14;
                elseif (isequal(subTypeSeq, [0 0 0 0]) || isequal(subTypeSeq, [1 0 0 0]))
                    subtype = 'Data/QoS Data';
                    if(IFSI(ii - 2) == 4 || IFSI(ii - 2) == 5)
                        IFSI(ii - 1) = 5;
                    else
                        IFSI(ii - 1) = 4;
                    end
                elseif(isequal(subTypeSeq, [0 1 0 0]))
                    subtype = 'Null data';
                    IFSI(ii - 1) = 6;
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

 save([fileName(1:end-4) '.mat'],'IFS','IFSI','locs','sampRate', 'accessCategory', 'IntDuration');

%%

  Load_and_Eval
  toc
