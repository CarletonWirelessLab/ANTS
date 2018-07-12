%packet detction
% Salime's Code, 26/2/2018
% 
% clear all
% clc
% close all
function [locs, Threshold1] = PacketDetection (fileName, sampRate, duration, ~)
%
% fileName = 'R1_R2_70M.bin';
% sampRate = 20e6;
% duration = .5;       % In seconds
% BW = 20;

fid = fopen(fileName , 'r');
rawData = fread(fid, 2 * sampRate * duration, 'float32');
iData = rawData(1:2:end);
qData = rawData(2:2:end);
cData = iData + 1j * qData;
Power = iData.^2 + qData.^2;

La = 50; %the size of winodw a, in samples
Lb = 50; %the size of winodw b, in samples

plen = length(Power);

BAPower = zeros(plen,1);
ABPower = zeros(plen,1);

for n=La:length(Power)-(Lb)

    Power_window_a =  sum(Power(n-La+1:n,1));
    Power_window_b =  sum(Power(n+1:n+Lb,1));
    
    BAPower(n,1) = Power_window_b / Power_window_a;
    ABPower(n,1) = Power_window_a / Power_window_b;
    
end

Threshold1 = 20;
Threshold2 = 20;

stmPos = (BAPower > Threshold1);
dif_stm = diff(stmPos);
stStrPos = find(dif_stm == 1) + 1;  % start of the start positions 
enStrPos = find(dif_stm == -1);     % end of the start positions 

enmPos = (ABPower > Threshold2);
dif_enm = diff(enmPos);
stEndPos = find(dif_enm == 1) + 1;  % start of the end positions 
enEndPos = find(dif_enm == -1);     % end of the end positions 

stmLen = length(stStrPos);
enmLen = length(stEndPos);

startPositions = zeros(stmLen,1);
endPositions = zeros(enmLen,1);
% 
% for k = 1:stmLen
%     [~,loc1] = max(BAPower(stStrPos(k):enStrPos(k)));
%     Index1 = (stStrPos(k):enStrPos(k))';
%     startPositions(k) = Index1(loc1);
% end

finThershold = 0.8;
for k = 1:stmLen
    [maxv] = max(BAPower(stStrPos(k):enStrPos(k)));
    Index1 = (stStrPos(k):enStrPos(k))';
    stindx = find(BAPower(stStrPos(k):enStrPos(k)) > maxv * finThershold);  % search amonge them for the 0.8 max
    startPositions(k) = Index1(stindx(end));   % take the highset index for starting position
end

for k = 1:enmLen
    [maxv] = max(ABPower(stEndPos(k):enEndPos(k)));
    Index2 = (stEndPos(k):enEndPos(k))';
    stindx = find(ABPower(stEndPos(k):enEndPos(k)) > maxv * finThershold);  % search amonge them for the 0.8 max
    endPositions(k) = Index2(stindx(1));  % take the lowest index for end position
end

if endPositions(1) < startPositions(1)
    endPositions(1) = []; end

if startPositions(end) > endPositions(end)
    endPositions(end+1) = plen; end


locs = [startPositions endPositions];

figure(2)
t = (0:(length(cData)-1))/sampRate;
indicator = zeros(size(t));
indicator(locs(:)) = 0.8 * max(abs(cData(:)));
plot(t, abs(cData), 'b-', t, indicator, 'r-');




