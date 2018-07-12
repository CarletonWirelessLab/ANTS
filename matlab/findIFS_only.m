close all; clear all;
fileName = 'FgTeast_t3.bin';
accessCategory = 2; % 0 = Voice, 1 = Video, 2 = Best Effort, 3 = BackGround
IntDuration = 0; % mSec

tic
sampRate = 20e6;
duration = inf;       % In seconds
packetIndex = 3;
f = 0.02;

% Find packetstart and end epochs
[locs, threshold] = detectPacketLocations(fileName, sampRate, duration,f); %Kareem's code
% [locs] = PacketDetection (fileName, sampRate, duration, 20); % Salime's Code

%symDurations = (locs(:, 2) - locs(:, 1))/sampRate * 1e6;
nVar = noiseVarEstimate(fileName, locs, duration, sampRate);
 
%packetInd = find(symDurations > 60);
IFS = (locs(2:end, 1) - locs(1:(end-1), 2))/sampRate * 1e6;

backOff = IFS;

%%

% ALL durations in one vector
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
% CPI = find(IFS > 25)'; %  4.2.7.3.2.4 Priority Classes, Guido's document
% TxopDurations = zeros(length(CPI),1);
% for ii = 2:length(CPI)
%      TxopDurations(ii-1) = (locs(CPI(ii),2) - locs(CPI(ii-1)+1,1));
% end
% TxopDurations(TxopDurations == 0) = [];
% TxopDurations = TxopDurations/sampRate * 1e3;  %mSec;
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
%
disp(['##' figName '#################################']);
disp(['- Found ', num2str(length(locs(:,1))), ' packets, ' num2str(length(IFS)) ' IFSs']);



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

%%%% Slilance Periods Data
CorrectBackOff = backOff(backOff > 27); % 27 uSec, Guido's recommendation

minBackOff = min(backOff)
textf = [num2str(floor(length(backOff)/2)) ' Samples']; % No of data packets is half the total (no RTS/CTS)
gtitle = ['X Histogram, Data silent periods, ' textf];
xlab = 'time (uSec)';
histScales(2, backOff, 100, gtitle, xlab, 1, [0 min(ceil(max(backOff)), 300)]);
saveas(gcf,['b_' figName '.jpg'])

%%%%% n

minCorrectBackOff = min(CorrectBackOff)
n = (CorrectBackOff - AIFS)/9;
textf = [num2str(length(n)) ' Samples'];
gtitle = ['Histogram, n BackOffs, ' textf];
xlab = 'n';
histScales(3, n, 100, gtitle, xlab, 1, [-1 max(max(ceil(max(n))+1,16))]);
saveas(gcf,['n_' figName '.jpg'])

%%%%  TXOP
% textf = [num2str(length(TxopDurations)) ' Samples'];
% gtitle = ['TXOP duration Histogram, ' textf];
% xlab = 'time (mSec)';
% histScales(4, TxopDurations, 50, gtitle, xlab, 0.05, [0 ceil(max(TxopDurations))]);
% saveas(gcf,['tx_' figName '.jpg'])

%%%% Compliance Calculator 
[Bins, prob , probMax, TxopDurations] = EN_301_893_ReqCalc(backOff, locs/sampRate * 1e6, accessCategory, 'Supervised');

meanTxop = mean(TxopDurations)
maxTxop = max(TxopDurations)