% Developer: Ammar Alhosainy, 13/03/2018
% Based on ETSI EN 301 893 V2.1.1 (2017-05), calssification of idle periods
% 5.4.9.3.2.4.1 steps 5 and 6

function [B, p, pMax, TxopDurations] = EN_301_893_ReqCalc(allBackOffs, locs, priorityClass)
% allBackOffs: A list of the backOff periods in (uSec)
% locs: Locations of the packets (uSec)
% priorityClass: 0 = Voice (Class 4), 1 = Video (Class 3), 2 = Best Effort (Class 2), 
% 3 = BackGround (Class 1)
% deviceClass: 'Supervising' or 'Supervised' not needed, deleted


BackOffs = allBackOffs(allBackOffs > 27); % 27 uSec, Guido's recommendation 


% Calculate TXOP (COT)

COT = find(allBackOffs > 25)'; %  4.2.7.3.2.4 Priority Classes, EN 301 893

TxopDurations = zeros(length(COT),1);
for ii = 2:length(COT)
    TxopDurations(ii-1) = (locs(COT(ii),2) - locs(COT(ii-1)+1,1));
end
TxopDurations(TxopDurations == 0) = [];
TxopDurations = TxopDurations/1e3;  %mSec;

% plot TXOP hist
figName = 'xx';
switch priorityClass
    case 0
        figName = 'vo';
    case 1
        figName = 'vi';
    case 2
        figName = 'be';
    case 3
        figName = 'bg';
end

textf = [num2str(length(TxopDurations)) ' Samples'];
gtitle = ['TXOP duration Histogram, ' textf];
xlab = 'time (mSec)';
histScales(4, TxopDurations, 50, gtitle, xlab, 0.05, [0 ceil(max(TxopDurations))]);
saveas(gcf,['tx_' figName '.jpg'])

slotTime = 9;
switch priorityClass
    case 0 % voice
        kp1 = 5;
            mind = 32;
            maxd = 59;       
    case 1 % video
        kp1 = 9;
            mind = 32;
            maxd = 95;
    case 2 % Best Effort
        kp1 = 17;
        mind = 41;
        maxd = 176;
    case 3 % Background
        kp1 = 17;
        mind = 77;
        maxd = 212;
end


% Classification of Idle Periods (B)
blen = length(BackOffs);
B = zeros(kp1,1);
for i = 1:blen
    x = BackOffs(i);
    if x < mind
        B(1) = B(1) + 1;
    elseif x >= maxd
        B(kp1) = B(kp1) + 1;
    else
        index = ceil((x-mind)/slotTime)+1;
        B(index) = B(index) + 1;
    end
end

% Calculate the observed cumulative probabilities (p)
E = blen;  % total observed periods
p = zeros(kp1,1);
pMax = p;

for ii = 1:kp1
    p(ii) = sum(B(1:ii))/E;
end

pMax(1) = 0.05;
pMax(kp1) = 1;
switch priorityClass
    case 0 % voice
        n = 1:3;
        pMax(n+1) = pMax(1) + n * 0.25;
    case 1 % video
        pMax(2) = 0.18;
        n = 2:6;  % the document says 2:6, could be a typo, I think it is 2:7
        pMax(n+1) = pMax(2) + (n-1) * 0.125;
        pMax(kp1-1) = 1;
    case {2, 3}
        pMax(2) = 0.12;
        n = 2:15;
        pMax(n+1) = pMax(2) + (n-1) * 0.0625;
end

%% Decision
if (sum(p > pMax))
    disp('(Unit does not Comply with the Standard)');
else
    disp('(Unit Complies with the Standard)');
end

%% Plot comparison with threshold
figure(3)
bar(0:kp1-1,[p pMax])
legend('Bin Probability','Compliance Upper threshold','Location','northwest')
title('Bin Probability and Threshold');
xlabel('Bin');
saveas(gcf,['prob_' figName '.jpg'])
