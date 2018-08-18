% Developer: Ammar Alhosainy, 13/06/2018
% Based on ETSI EN 301 893 V2.1.1 (2017-05), calssification of idle periods
% 5.4.9.3.2.4.1 steps 5 and 6

function [SIFSFactor, TxopFactor, AGFactor, KBL, NF] = ComplianceMetric_v101(allBackOffs, SIFSD, locs, priorityClass, deviceClass)
% allBackOffs: A list of the backOff periods in (uSec)
% locs: Locations of the packets (uSec)
% priorityClass: 0 = Voice (Class 4), 1 = Video (Class 3), 2 = Best Effort (Class 2), 
% 3 = BackGround (Class 1)
% deviceClass: 'Supervising' or 'Supervised'

if (deviceClass ~= 'Supervised') & (priorityClass < 2)
   BackOffs = allBackOffs(allBackOffs > 18); % (27-9) uSec, Ammar's recommendation
else
   BackOffs = allBackOffs(allBackOffs > 27); % 27 uSec, Guido's recommendation 
end

% Calculate TXOP (COT)
if (deviceClass ~= 'Supervised') & (priorityClass < 2)
    COT = find(allBackOffs > 23)'; %  Ammar's recommendation
else
    COT = find(allBackOffs > 25)'; %  4.2.7.3.2.4 Priority Classes, EN 301 893
end

TxopDurations = zeros(length(COT),1);
for ii = 2:length(COT)
    TxopDurations(ii-1) = (locs(COT(ii),2) - locs(COT(ii-1)+1,1));
end
TxopDurations(TxopDurations == 0) = [];
TxopDurations = TxopDurations/1e3;  %mSec;

% Standard ETSI.
slotTime = 9;
TxopLimit = 0;
figName = 'xx';
switch priorityClass
    case 0
        TxopLimit = 2;
        AIFS = 34;
        N = 4;
        figName = 'vo';
    case 1
        TxopLimit = 4;
        AIFS = 34;
        N = 8;
        figName = 'vi';
    case 2
        TxopLimit = 6;
        AIFS = 43;
        N = 16;
        figName = 'be';
    case 3
        TxopLimit = 6;
        AIFS = 79;
        N = 16;
        figName = 'bg';
end

% LIMITS SET BY AMMAR
if (deviceClass ~= 'Supervised') & (priorityClass < 2)
    BFmin = AIFS - slotTime/2 - slotTime;
    BFmax = AIFS + slotTime*(N-1) + slotTime/2 - slotTime;
else
    BFmin = AIFS - slotTime/2;
    BFmax = AIFS + slotTime*(N-1) + slotTime/2;
end

% LIMITS SET BY ETSI
% if (deviceClass ~= 'Supervised') & (priorityClass < 2)
%     BFmin = AIFS - 2 - slotTime;
%     BFmax = AIFS + slotTime*(N-1) + 7 - slotTime;
% else
%     BFmin = AIFS - 2;
%     BFmax = AIFS + slotTime*(N-1) + 7;
% end
BFmid = (BFmax + BFmin)/2;

%% TXOP compliance factor
PacketsDurations = (locs(:, 2) - locs(:, 1));
maxPacketDuration = max(PacketsDurations)/1e3;

if TxopLimit == 0
    violatingDurations  = TxopDurations(TxopDurations > maxPacketDuration);
else
    violatingDurations  = TxopDurations(TxopDurations > TxopLimit);
end
TxopFactor = (length(violatingDurations)/length(TxopDurations))


%% Classification of Idle Periods (B)
blen = length(BackOffs);
B = zeros(N,1);
for i = 1:blen
    x = BackOffs(i);
    if x <= BFmin
        B(1) = B(1) + 1;
    elseif x >= BFmax
        B(N) = B(N) + 1;
    else
        index = ceil((x-BFmin)/slotTime);
        B(index) = B(index) + 1;
    end
end

prob = B/sum(B);
nzProb = prob(prob > 0);  % non zero prob.

KBL = -sum(nzProb .* log10(nzProb/(1/N)))
DistFactor = 1 - exp(KBL)

%% Agressivness factor (AGF) (+ve = agressive, -ve = submissive)
% acumMeasurB(1) = B(1);
% acumIdealB(1) = blen/N;
% for ii = 2:N
%     acumMeasurB(ii) = sum(B(1:ii));
%     acumIdealB(ii) = acumIdealB(ii-1) + blen/N;
% end
% 
% BIdeal = ones(N,1) * blen/N;
% 
% overNumber = 0;
% underNumer = 0;
% overIndex = (acumMeasurB > acumIdealB);
% underIndex = acumMeasurB <= acumIdealB;
% if (sum(overIndex))
%     disp('(Unit is Aggressive)');
%     AGFactor = (sum(acumMeasurB(overIndex) - acumIdealB(overIndex))+ acumMeasurB(end))/sum(acumIdealB)
%     %AGFactor = overNumer/blen;
% else
%     disp('(Unit is Submissive)');
%     AGFactor = sum(acumMeasurB(underIndex) - acumIdealB(underIndex))/sum(acumIdealB)
%     %AGFactor = underNumer/blen;
% end
% 
% figure(21)
% bar(1:N,[acumMeasurB'/blen acumIdealB'/blen])

% OLD IDEA
%BackOffs = BackOffs(BackOffs < BFmax);  
% meanIFS = mean(BackOffs);
% AGFactor = (BFmid - mean(BackOffs))/(BFmid - BFmin)
% 
% if AGFactor > 0
%     disp('(Unit is Aggressive)');
% else
%     disp('(Unit is Submissive)');
% end

accum = sum((B).* ((N-1)/2:-1:-(N-1)/2)');
avrg = accum / blen;
mid = (N-1)/2;
AGFactor = (avrg)/mid

%% SIFS compliance factor

if (deviceClass ~= 'Supervised') & (priorityClass < 2)
    SIFSs = SIFSD(SIFSD < 18); % (27-9) uSec, Ammar's recommendation
else
    SIFSs = SIFSD(SIFSD < 16 + 9/2); % between 16 and PIFS, grater the RIFS
end
SIFSs = SIFSs(SIFSs > 4);

SIFSFactor = (mean(SIFSs) - 16)/16
%% Norm Factor
NF = sqrt(AGFactor^2 + TxopFactor^2 + DistFactor^2 + SIFSFactor^2)/2
NFP = (1 - NF)*100;

%% Geometric mean Factor
GF = ((1 - abs(AGFactor)) * (1 - TxopFactor) * (1 - DistFactor) * (1 - abs(SIFSFactor)))^(1/4)

%% Decision
if AGFactor > 0
    disp(['%',num2str(abs(AGFactor)*100), ' Aggressive, %', num2str(NFP), ' Compliant'] );
else
    disp(['%',num2str(abs(AGFactor)*100), ' Submissive, %', num2str(NFP), ' Compliant'] );
end

