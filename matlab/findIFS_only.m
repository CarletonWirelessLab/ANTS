fileName = 'TP_LinkAP_AsusUSB42_0x80.bin';
accessCategory = 2; % 0 = Voice, 1 = Video, 2 = Best Effort, 3 = BackGround
IntDuration = 0; % mSec
mode = 'Supervisey';
sampRate = 20e6;
duration = inf;       % In seconds
packetIndex = 3;
f = 0.02;
% Find packetstart and end epochs
[locs, threshold] = detectPacketLocations(fileName, sampRate, duration,f); %Kareem's code
IFS = (locs(2:end, 1) - locs(1:(end-1), 2))/sampRate * 1e6;
backOff = IFS;
%% Save Output
save([fileName(1:end-4) '.mat'],'IFS','locs','sampRate', 'accessCategory', 'IntDuration', 'mode');

Load_and_Eval_IFSOnly
 
