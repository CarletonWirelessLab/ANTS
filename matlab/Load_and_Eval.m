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

DataReCount = sum(IFSI == 14);
DataReIDs = find(IFSI == 14) + 1;
DataReIFS = IFS(DataReIDs - 1);

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

%%% ALL durations in one vector
PacketsDurations = (locs(:, 2) - locs(:, 1))/sampRate * 1e3;
dataPacketDuration = PacketsDurations(PacketsDurations > 0.5); % 0.5 mSec
cn = 1;
for i = 1:length(locs)-1
   alld(cn) = locs(i,2) - locs(i,1);
   alld(cn+1) = locs(i+1,1) - locs(i,2);
   cn = cn + 2;
end
alld = alld'/sampRate * 1e6;

% 
% 
% CPI = find(IFS > 25)'; %  4.2.7.3.2.4 Priority Classes, Guido's document
% TxopDurations = zeros(length(CPI),1);
% for ii = 2:length(CPI)
%     if (IFSI(CPI(ii-1)) == 4 ||IFSI(CPI(ii-1)) == 5 ||IFSI(CPI(ii-1)) == 7)
%         TxopDurations(ii-1) = (locs(CPI(ii),2) - locs(CPI(ii-1)+1,1));
%     end
% end
% TxopDurations(TxopDurations == 0) = [];
% TxopDurations = TxopDurations/sampRate * 1e3;  %mSec;

%
disp('#####################################');
disp(['- Found ', num2str(length(locs(:,1))), ' packets, ' num2str(length(IFS)) ' IFSs']);
disp(['- Acks/BAs = ', num2str(ACKCount)]);
disp(['- RTS/CTSs = ', num2str(RTSCount), '/' , num2str(CTSCount)]);
disp(['- BAR = ', num2str(BARCount)]);
disp(['- Beacons = ', num2str(BeaconsCount)]);
disp(['- Data (no back to back) = ', num2str(DataCount)]);
disp(['- Data (back to back) = ', num2str(b2bDataCount)]);
disp(['- Data Retransmission = ', num2str(DataReCount)]);
disp(['- Null Data = ', num2str(nullDataCount)]);
disp(['- Unknown = ', num2str(unknownCount)]);
disp(['- Unwanted Data = ', num2str(unwantedDataCount)]);


%

SIFS = mean(IFS(IFSI == 1))

frameControlField = IFS(IFSI == 2);
PIFS = mean(frameControlField)

allDataBackOff = IFS(IFSI == 4 | IFSI == 5 | IFSI == 7);  % Data, b2b Data & RTS


figName = 'xx';
switch accessCategory
    case 0
        figName = 'vo';
    case 1
        figName = 'vi';
    case 2
        figName = 'be';
    case 3
        figName = 'bg';
end


    
%%%% Slilance Periods Data

minBackOff = min(allDataBackOff)
textf = [num2str(length(allDataBackOff)) ' Samples'];
gtitle = ['X Histogram, Data silent periods, ' textf];
xlab = 'time (uSec)';
histScales(2, allDataBackOff, 150, gtitle, xlab, 1, [0 max(ceil(max(allDataBackOff)), 100)]);
saveas(gcf,['b_' figName '.jpg'])

%%%%% n
CorrectBackOff = allDataBackOff(allDataBackOff > 27); % 27 uSec, Guido's recommendation
minCorrectBackOff = min(CorrectBackOff)
n = (CorrectBackOff - AIFS)/9;
textf = [num2str(length(n)) ' Samples'];
gtitle = ['Histogram, n BackOffs, ' textf];
xlab = 'n';
histScales(3, n, 0, gtitle, xlab, 1, [-1 max(max(ceil(max(n))+1,16))]);
saveas(gcf,['n_' figName '.jpg'])

    
if (DataReCount > 50)
    %%%% Slilance Periods Data Retransmission
    backOffRE = IFS(IFSI == 14);
    DataRe_minBackOff = min(backOffRE)
    textf = [num2str(length(backOffRE)) ' Samples'];
    gtitle = ['X Histogram, ReTX Data silent periods, ' textf];
    xlab = 'time (uSec)';
    histScales(12, backOffRE, 0, gtitle, xlab, 1, [0 max(ceil(max(backOffRE)), 300)]);
    saveas(gcf,['re_b_' figName '.jpg'])


    %%%%% n Data Retransmission
    CorrectBackOffRE = backOffRE(backOffRE > 27); % 27 uSec, Guido's recommendation
    minCorrectReTx_BackOff = min(CorrectBackOffRE)
    n = (CorrectBackOffRE - AIFS)/9;
    textf = [num2str(length(n)) ' Samples'];
    gtitle = ['n Histogram, ReTX BackOffs, ' textf];
    histScales(13, n, 0, gtitle, 'n', 1, [-1 max(max(ceil(max(n))+1,16))]); 
    saveas(gcf,['re_n_' figName '.jpg'])

end
% 
% textf = [num2str(length(TxopDurations)) ' Samples'];
% gtitle = ['TXOP duration Histogram, ' textf];
% xlab = 'time (mSec)';
% histScales(4, TxopDurations, 50, gtitle, xlab, 0.05, [0 ceil(max(TxopDurations))]);
% saveas(gcf,['tx_' figName '.jpg'])

%%%% Compliance Calculator 
[Bins, prob , probMax, TxopDurations] = EN_301_893_ReqCalc(allDataBackOff, locs/sampRate * 1e6, accessCategory, 'Supervised');

meanTxop = mean(TxopDurations)
maxTxop = max(TxopDurations)
