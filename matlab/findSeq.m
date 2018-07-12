function startPos = findSeq(longSeq, shortSeq)

shortLen = length(shortSeq);
longLen = length(longSeq);
startPos = zeros(1, longLen);
jj = 0;
for ii = 0:(longLen - shortLen)
    crtSeq = longSeq(ii + (1:shortLen));
    if(isequal(crtSeq, shortSeq))
        jj = jj + 1;
        startPos(jj) = ii + 1;
    end
end
startPos = startPos(logical(startPos));
