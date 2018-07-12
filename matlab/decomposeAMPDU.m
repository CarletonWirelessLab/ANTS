function [MPDUinfo] = decomposeAMPDU(payLoad)
%AMDPUinfo has PacketID, state, FragmentNumber, SeqID, Retrybit

%Define Checksum object
H = comm.CRCDetector([8 2 1 0], 'InitialConditions', 1, 'DirectMethod', true, 'FinalXOR', true);

start = 0;
MPDUinfo = 0;
payLoadlen = length(payLoad);
payLoad = logical(payLoad)';
ID = 1;
while(start < payLoadlen - 32)
    % Look for the MPDU delimiter
    MPDUDelimiter = payLoad(start + (1:32));
    [~, crcErrorBit] = step(H, MPDUDelimiter(1:24)');
    signatureBitCheck = biterr(MPDUDelimiter(25:32), [0 1 1 1 0 0 1 0]);
    if(~crcErrorBit && ~signatureBitCheck) % Passed!
        MPDUHeader = payLoad(start + 32 + (1:288));
        
        % Get FragmentNumber, SeqID, Retrybit from MPDU header
        % Get Tx add, Rx Add and packet type from first packet
        packet.ID = ID;
        packet.Retrybit = MPDUHeader(12);
        packet.FragN = double(bi2de(logical(MPDUHeader(176 + (1:4)))));
        packet.SeqN = double(bi2de(logical(MPDUHeader(176 + (5:16)))));
        
        % return the info here
        MPDUinfo = 0;
        
        ID = ID + 1;
        packetLen = sum(MPDUDelimiter(5:16) .* 2.^(3:14)) +32;
        
        start = start + packetLen;
    else
        ii = 1;
        while (start + ii < payLoadlen - 32)
            potentialMPDUDelimiter = payLoad(start + ii:start + ii + 32);
            signatureBitCheck = biterr(potentialMPDUDelimiter(25:32), [0 1 1 1 0 0 1 0]);
            if(~signatureBitCheck)
                [~, crcErrorBit] = step(H, potentialMPDUDelimiter(1:24)');
                if (~crcErrorBit)
                    
                    break;
                end
            end
            ii = ii + 32;
        end
        start = start + ii - 1;
    end
end
