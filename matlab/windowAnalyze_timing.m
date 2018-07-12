% Added packets timing to the output

%clc; 

close all; %clear all;
fileName = 'AP11_to_AsusUsb42_QoS_0xVi_100M.bin';
nullingTime = 1e-3;
sampRate = 20e6;
duration = inf;       % In seconds
packetIndex = 3;
f = 0.01;
% Find packetstart and end epochs
[locs, threshold] = detectPacketLocations(fileName, sampRate, duration, f); % Kareem's code

% [locs, threshold] = PacketDetection (fileName, sampRate, duration, f); % Salime's Code


%nVar = noiseVarEstimate(fileName, locs, duration, sampRate);
%nVar = 1.670439341361422e-5;
% Fetch the first packet
fid = fopen(fileName , 'r');
rawData = fread(fid, 2 * sampRate * duration, 'float32');
iData = rawData(1:2:end);
qData = rawData(2:2:end);
cData = iData + 1j * qData;

for ii = 2:length(locs)
    packet =  1 * cData(locs(ii, 1):locs(ii, 2));
    disp(['Packet #' char(string(ii)) ':'])
    [~, payLoad1, MACAggregation] = packetDecode(packet, 20, sampRate, 1e-6);
    if(MACAggregation)
        disp('- Aggregation is on')
        payLoad = payLoad1(33:end); % Skip the first 32 bits
        %payLoad1(1:32)'
        %keyboard;
    else
        disp('- Aggregation is off')
        payLoad =  payLoad1;
    end
    
    temp = payLoad(1:16)';
    subTypeSeq = temp(8:-1:5);
    if(isequal(temp(1:2),  zeros(1, 2)))
          if(isequal(temp(3:4), zeros(1,2)))
              type = 'management';
              
              if(isequal(subTypeSeq, [0 0 0 0]))
                  subtype = 'Association Request';
              elseif(isequal(subTypeSeq, [0 0 0 1]))
                  subtype = 'Association Response';
              elseif(isequal(subTypeSeq, [0 0 1 0]))
                  subtype = 'Reassociation Request';
              elseif(isequal(subTypeSeq, [0 0 1 1]))
                  subtype = 'Reassociation Response';
              elseif(isequal(subTypeSeq, [0 1 0 0]))
                  subtype = 'Probe Request';
              elseif(isequal(subTypeSeq, [0 1 0 1]))
                  subtype = 'Probe Response';
              elseif(isequal(subTypeSeq, [0 1 1 0]))
                  subtype = 'Reserved';
              elseif(isequal(subTypeSeq, [0 1 1 1]))
                  subtype = 'Reserved';
              elseif(isequal(subTypeSeq, [1 0 0 0]))
                  subtype = 'Beacon';
              elseif(isequal(subTypeSeq, [1 0 0 1]))
                  subtype = 'ATIM';
              elseif(isequal(subTypeSeq, [1 0 1 0]))
                  subtype = 'Deassociation';
              elseif(isequal(subTypeSeq, [1 0 1 1]))
                  subtype = 'Authentication';
              elseif(isequal(subTypeSeq, [1 1 0 0]))
                  subtype = 'Deauthentication';
              elseif(isequal(subTypeSeq, [1 1 0 1]))
                  subtype = 'Action';
              elseif(isequal(subTypeSeq, [1 1 1 0]))
                  subtype = 'Action no ACK';
              elseif(isequal(subTypeSeq, [1 1 1 1]))
                  subtype = 'Reserved';
              end
              
          elseif(isequal(temp(3:4), [1 0]))
              type = 'control';
              
              if(isequal(subTypeSeq, [0 0 0 0]))
                  subtype = 'Reserved';
              elseif(isequal(subTypeSeq, [0 0 0 1]))
                  subtype = 'Reserved';
              elseif(isequal(subTypeSeq, [0 0 1 0]))
                  subtype = 'Reserved';
              elseif(isequal(subTypeSeq, [0 0 1 1]))
                  subtype = 'Reserved';
              elseif(isequal(subTypeSeq, [0 1 0 0]))
                  subtype = 'Beamforming';
              elseif(isequal(subTypeSeq, [0 1 0 1]))
                  subtype = 'VHT NDP announcement';
              elseif(isequal(subTypeSeq, [0 1 1 0]))
                  subtype = 'Reserved';
              elseif(isequal(subTypeSeq, [0 1 1 1]))
                  subtype = 'Control Wrapper';
              elseif(isequal(subTypeSeq, [1 0 0 0]))
                  subtype = 'BAR';
              elseif(isequal(subTypeSeq, [1 0 0 1]))
                  subtype = 'BA';
              elseif(isequal(subTypeSeq, [1 0 1 0]))
                  subtype = 'PS-Poll';
              elseif(isequal(subTypeSeq, [1 0 1 1]))
                  subtype = 'RTS';
              elseif(isequal(subTypeSeq, [1 1 0 0]))
                  subtype = 'CTS';
              elseif(isequal(subTypeSeq, [1 1 0 1]))
                  subtype = 'ACK';
              elseif(isequal(subTypeSeq, [1 1 1 0]))
                  subtype = 'CF-END';
              elseif(isequal(subTypeSeq, [1 1 1 1]))
                  subtype = 'CF-END + CF-ACK';
              end
          elseif(isequal(temp(3:4), [0 1]))
              type = 'data';
              
              if(isequal(subTypeSeq, [0 0 0 0]))
                  subtype = 'Data';
              elseif(isequal(subTypeSeq, [0 0 0 1]))
                  subtype = 'Data + CF-ACK';
              elseif(isequal(subTypeSeq, [0 0 1 0]))
                  subtype = 'Data + CF-Poll';
              elseif(isequal(subTypeSeq, [0 0 1 1]))
                  subtype = 'Data + CF-ACK + CF-Poll';
              elseif(isequal(subTypeSeq, [0 1 0 0]))
                  subtype = 'Null data';
              elseif(isequal(subTypeSeq, [0 1 0 1]))
                  subtype = 'CF-ACK';
              elseif(isequal(subTypeSeq, [0 1 1 0]))
                  subtype = 'CF-Poll';
              elseif(isequal(subTypeSeq, [0 1 1 1]))
                  subtype = 'CF-ACK + CF-Poll';
              elseif(isequal(subTypeSeq, [1 0 0 0]))
                  subtype = 'QOS data';
              elseif(isequal(subTypeSeq, [1 0 0 1]))
                  subtype = 'QOS data + CF-ACK';
              elseif(isequal(subTypeSeq, [1 0 1 0]))
                  subtype = 'QOS data + CF-Poll';
              elseif(isequal(subTypeSeq, [1 0 1 1]))
                  subtype = 'QOS data + CF-ACK + CF-Poll';
              elseif(isequal(subTypeSeq, [1 1 0 0]))
                  subtype = 'QOS Null';
              elseif(isequal(subTypeSeq, [1 1 0 1]))
                  subtype = 'Reserved';
              elseif(isequal(subTypeSeq, [1 1 1 0]))
                  subtype = 'QOS CF-Poll';
              elseif(isequal(subTypeSeq, [1 1 1 1]))
                  subtype = 'QOS CF-ACK + CF-Poll';
              end
          else
              type = 'unidentified';
              subtype = 'unidentified';
          end
          disp(['type is ' type ' subtype is ' subtype '.'])
          try
             disp(['Rx Add = ' getMAC(payLoad(32 + (1:48))) ',    Tx Add = ' getMAC(payLoad(80 + (1:48))) '.']) 
          catch
              disp(['Rx Add = ' getMAC(payLoad(32 + (1:48)))]);
          end
    else
        disp('- Packet is unidentified.')
    end
    
    before = (locs(ii, 1)-locs(ii-1, 2))/sampRate*1e6;
    after = (locs(ii+1, 1)-locs(ii, 2))/sampRate*1e6;
    disp(['Period Before = ' num2str(before) ',   After = ' num2str(after) ' uSec']);
    disp(['Start = ' num2str(locs(ii, 1)/sampRate*1e3) ', End = ' num2str(locs(ii, 2)/sampRate*1e3) ', duration = ' num2str((locs(ii, 2)-locs(ii, 1))/sampRate*1e6) ' uSec']);
    
    if (before < 20 && after < 20)
        1
    end
    
    disp('===============================================')

    keyboard
end