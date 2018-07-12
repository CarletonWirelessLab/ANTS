%packet detction
% Salime's Code, 26/2/2018

function [locs, threshold] = PacketDetection (fileName, sampRate, duration, ~)


fid = fopen(fileName , 'r');
rawData = fread(fid, 2 * sampRate * duration, 'float32');
iData = rawData(1:2:end);
qData = rawData(2:2:end);
cData = iData + 1j * qData;
Power = iData.^2 + qData.^2;

La = 50; %the size of winodw a, in samples
Lb = 50; %the size of winodw b, in samples

BAPower = zeros(length(Power),1);
ABPower = zeros(length(Power),1);

Power_window_a =  sum(Power(1:La));
Power_window_b =  sum(Power(La+1:La+Lb));

BAPower(La) = Power_window_b/Power_window_a;
ABPower(La) = Power_window_a/Power_window_b;

for n=1:length(Power)-(La+Lb)
   
    Power_window_a = Power_window_a - Power(n) + Power(La+n);
    Power_window_b = Power_window_b - Power(La+n) + Power(La+Lb+n);
    
    BAPower(La+n,1) = Power_window_b/Power_window_a;
    ABPower(La+n,1) = Power_window_a/Power_window_b;
    
end
% 
% for n=La:length(Power)-(Lb)
% 
%     Power_window_a =  sum(Power(n-La+1:n));
%     Power_window_b =  sum(Power(n+1:n+Lb));
%     
%     BAPower(n) = Power_window_b/Power_window_a;
%     ABPower(n) = Power_window_a/Power_window_b;
%     
% end

Threshold1 = 20;
Threshold2 = 20;

x1 = (BAPower > Threshold1);
dif_x1 = diff(x1);
start_index1 = find(dif_x1 == 1)+1;
end_index1 = find(dif_x1 == -1);

x2 = (ABPower > Threshold2);
dif_x2 = diff(x2);
start_index2 = find(dif_x2 == 1)+1;
end_index2 = find(dif_x2 == -1);

sumdif1 = sum(dif_x1==1);
sumdif2 = sum(dif_x2==1);

finThershold = 0.8;
for k = 1:max(sumdif1,sumdif2)

    if k<=sumdif1
        [maxv] = max(BAPower(start_index1(k):end_index1(k)));
        Index1 = (start_index1(k):end_index1(k))';
        stindx = find(BAPower(start_index1(k):end_index1(k)) > maxv * finThershold);  % search amonge them for the 0.8 max
        Locs_start(k,1) = Index1(stindx(end));
    end
    
    if k<=sumdif2
        [maxv] = max(ABPower(start_index2(k):end_index2(k)));
        Index2 = (start_index2(k):end_index2(k))';
        stindx = find(ABPower(start_index2(k):end_index2(k)) > maxv * finThershold);  % search amonge them for the 0.8 max
        Locs_end(k,1) = Index2(stindx(1));
    end
end

first_start = Locs_start(1,1);
last_end = Locs_end(end,1);

d1 = find(Locs_end < first_start);
Locs_end(d1)= [];

d2 = find(Locs_start > last_end);
Locs_start(d2) = [];


s1 = length(Locs_start); s2 = length(Locs_end);
M1 = min(s1,s2);
D = find (Locs_end(1:M1)<Locs_start(1:M1));

while ~isempty(D)
    if s1 < s2
        Locs_end(D(1)) = [];
    elseif s1 > s2
        Locs_start(D(1)) = [];
    end
    M1 = min(length(Locs_start),length(Locs_end));
    D = find (Locs_end(1:M1) < Locs_start(1:M1));
    
end
M1 = min(length(Locs_start),length(Locs_end));
Locs = [Locs_start(1:M1),Locs_end(1:M1)];


locs = Locs;
threshold = Threshold1;

figure(2)
t = (0:(length(cData)-1))/sampRate;
indicator = zeros(size(t));
indicator(locs(:)) = 0.8 * max(abs(cData(:)));
plot(t, abs(cData), 'b-', t, indicator, 'r-');




