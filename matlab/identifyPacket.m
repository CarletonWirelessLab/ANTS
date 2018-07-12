function identifyPacket(fileName , packetIDs, f)
sampRate = 20e6;
duration = inf;
% Read data
fid = fopen(fileName , 'r');
rawData = fread(fid, 2 * sampRate * duration, 'float32');
iData = rawData(1:2:end);
qData = rawData(2:2:end);
cData = iData + 1j * qData;

% Detect packets
[locs, ~] = detectPacketLocations(fileName, sampRate, duration, f);

packetIDsLength = length(packetIDs);
% Extract the specified packet
for ii = 1:packetIDsLength
    packet = cData(locs(packetIDs(ii), 1):locs(packetIDs(ii), 2));
    
    disp(['Packet #' num2str(packetIDs(ii)) ':'])
    try
        [frmt, payLoad1, MACAggregation] = packetDecode(packet, 20, sampRate, 1e-6);
    catch
        disp(['Runtime Error: Packet decoding failed!!']);
        disp('===============================================')
        continue;
    end
    if(MACAggregation)
        payLoad = payLoad1(33:end);
    else
        payLoad = payLoad1;
    end
    
    frameControlField = payLoad(1:16)';
    subTypeSeq = frameControlField(8:-1:5);
    if(isequal(frameControlField(1:2),  zeros(1, 2)))
        if(isequal(frameControlField(3:4), zeros(1,2)))
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
            
        elseif(isequal(frameControlField(3:4), [1 0]))
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
        elseif(isequal(frameControlField(3:4), [0 1]))
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
            if(payLoad(12))
                disp('Retransmission? Yes')
            else
                disp('Retransmission? No')
            end
        else
            disp('Unknown type!!');
            disp('===============================================')
            continue;
        end
        disp(['type is ' type ' subtype is ' subtype '.'])
        try
            disp(['Rx Add = ' getMAC(payLoad(32 + (1:48))) ',    Tx Add = ' getMAC(payLoad(80 + (1:48))) '.'])
            if(strcmp(type, 'data'))
                seqControl = payLoad(22 * 8 + (1:16));
                fragID = bi2de(seqControl(1:4)');
                seqID = bi2de(seqControl(5:16)');
                disp(['Fragment Number = ' num2str(fragID) ', Sequence Number = ' num2str(seqID)]);
            end
        catch
            disp(['Rx Add = ' getMAC(payLoad(32 + (1:48)))]);
        end
    else
        disp('Protocol Version Mismatch - Packet is unidentified.')
    end
    disp('===============================================')
end