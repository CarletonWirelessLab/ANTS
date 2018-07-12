function nVar = noiseVarEstimate(fileName, locs, duration, sampRate)


fid = fopen(fileName , 'r');
rawData = fread(fid, 2 * sampRate * duration, 'float32');
iData = rawData(1:2:end);
qData = rawData(2:2:end);

idl = length(iData);
qdl = length(qData);

if     idl > qdl
        iData = iData(1:qdl);
elseif qdl > idl
        qData = qData(1:idl);
end

cData = iData + 1j * qData;

packetsNum = length(locs);
noiseVecIndices = zeros(size(cData));
startInd = 0;
for ii = 2:packetsNum
    windowLength = locs(ii, 1) - locs(ii - 1, 2) - 39;
    noiseVecIndices(startInd + (1:windowLength)) = (locs(ii - 1,2) + 20):(locs(ii, 1) - 20);
    startInd = startInd + windowLength;
end
noiseVecIndices = noiseVecIndices(1:startInd);

nVar = mean(abs(cData(noiseVecIndices)).^2);

% figure
% plot(abs(cData(noiseVecIndices)).^2)