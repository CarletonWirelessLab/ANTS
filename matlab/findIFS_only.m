close all; clear all;

fileName = 'TP_LinkAP_AsusUSB42_0x80.bin';
accessCategory = 2; % 0 = Voice, 1 = Video, 2 = Best Effort, 3 = BackGround
IntDuration = 0; % mSec

mode = 'Supervisey';
% mode = 'Supervisey';

sampRate = 20e6;
duration = inf;       % In seconds
packetIndex = 3;
f = 0.02;

% Find packetstart and end epochs
[locs, threshold] = detectPacketLocations(fileName, sampRate, duration,f); %Kareem's code
% [locs] = PacketDetection (fileName, sampRate, duration, 20); % Salime's Code
 
%packetInd = find(symDurations > 60);
IFS = (locs(2:end, 1) - locs(1:(end-1), 2))/sampRate * 1e6;

backOff = IFS;

%%

% ALL durations in one vector
% PacketsDurations = (locs(:, 2) - locs(:, 1))/sampRate * 1e3;
% dataPacketDuration = PacketsDurations(PacketsDurations > 0.5); % 0.5 mSec
% cn = 1;
% for i = 1:length(locs)-1
%    alld(cn) = locs(i,2) - locs(i,1);
%    alld(cn+1) = locs(i+1,1) - locs(i,2);
%    cn = cn + 2;
% end
% alld = alld'/sampRate * 1e6;


%% Save Output

 save([fileName(1:end-4) '.mat'],'IFS','locs','sampRate', 'accessCategory', 'IntDuration', 'mode');

%%

  Load_and_Eval_IFSOnly


