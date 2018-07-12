%packet detction
% Salime's Code, 26/2/2018
% 
% clear all
% clc
% close all
% function [locs, threshold] = PacketDetection (fileName, sampRate, duration, f)
%
fileName = 'Chamber_5M_1.bin';
sampRate = 20e6;
duration = .005;       % In seconds
BW = 20;

fid = fopen(fileName , 'r');
rawData = fread(fid, 2 * sampRate * duration, 'float32');
iData = rawData(1:2:end);
qData = rawData(2:2:end);
cData = iData + 1j * qData;
Power = iData.^2 + qData.^2;

La = 50; %the size of winodw a, in samples
Lb = 50; %the size of winodw b, in samples

m1 = zeros(length(Power),1);
m2 = zeros(length(Power),1);

Power_window_a =  sum(Power(1:La,1));
Power_window_b =  sum(Power(La+1:La+Lb,1));

m1(La,1) = Power_window_b/Power_window_a;
m2(La,1) = Power_window_a/Power_window_b;

for n=1:length(Power)-(La+Lb)
   
    Power_window_a = Power_window_a - Power(n,1) + Power(La+n,1);
    Power_window_b = Power_window_b - Power(La+n,1) + Power(La+Lb+n,1);
    
%     Power_window_a1 =  sum(Power(1+n:n+La,1));
%     Power_window_b1 =  sum(Power(n+La+1:n+La+Lb,1));
    
    m1(La+n,1) = Power_window_b/Power_window_a;
    m2(La+n,1) = Power_window_a/Power_window_b;
    
end
figure
x = 0:length(Power)-1;
subplot(2,1,1), plot(Power)
subplot(2,1,2), plot( x,min(m1,500), 'r-',x,min(m2,500), 'b-')


Threshold1 = 100;
x1 = (m1>Threshold1);
dif_x1 = diff(x1);

start_index1 = find(dif_x1 == 1)+1;
end_index1 = find(dif_x1 == -1);



Threshold2 = 100;
x2 = (m2>Threshold2);
dif_x2 = diff(x2);

start_index2 = find(dif_x2 == 1)+1;
end_index2 = find(dif_x2 == -1);

sumdif1 = sum(dif_x1==1);
sumdif2 = sum(dif_x2==1);

%sum(dif_x1==1),sum(dif_x2==1)
for k = 1:max(sumdif1,sumdif2)

    if k<=sumdif1
        [max1,loc1] = max(m1(start_index1(k):end_index1(k)));
        Index1 = (start_index1(k):end_index1(k))';
        Locs_start(k,1) = Index1(loc1);
    end
    
    if k<=sumdif2
        [max2,loc2] = max(m2(start_index2(k):end_index2(k)));
        Index2 = (start_index2(k):end_index2(k))';
        Locs_end(k,1) = Index2(loc2);
    end
end

first_start = Locs_start(1,1);
last_end = Locs_end(end,1);

d1 = find(Locs_end<first_start);
Locs_end(d1)= [];

d2 = find(Locs_start>last_end);
Locs_start(d2) = [];


s1 = length(Locs_start); s2 = length(Locs_end);
M1 = min(s1,s2);
D = find (Locs_end(1:M1)<Locs_start(1:M1));

while length(D)>0
    if s1<s2
        Locs_end(D(1)) = [];
    elseif s1>s2
        Locs_start(D(1)) = [];
    end
    M1 = min(length(Locs_start),length(Locs_end));
    D = find (Locs_end(1:M1)<Locs_start(1:M1));
    
end
M1 = min(length(Locs_start),length(Locs_end));
Locs = [Locs_start(1:M1),Locs_end(1:M1)];


locs = Locs;
threshold = Threshold1;
% save('Locations_Chamber_5M_1.mat','Locs')




