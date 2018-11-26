#Author Xinrui Zhang
#Based on ETSI EN 301 893 V2.1.1 (2017-05), calssification of idle periods
import math
import numpy as np
import matplotlib.pyplot as plt
# 5.4.9.3.2.4.1 steps 5 and 6
def EN_301_893_ReqCalc(allBackOffs, locs, priorityClasss):
    # allBackOffs: A list of the backOff periods in (uSec)
    # locs: Locations of the packets (uSec)
    # priorityClass: 0 = Voice (Class 4), 1 = Video (Class 3), 2 = Best Effort (Class 2),
    # 3 = BackGround (Class 1)

    #27 uSec, Guido's recommendation
    #BackOffs = allBackOffs(allBackOffs > 27)
    BackOffs = [x for x in allBackOffs if x >27]

    # Calculate TXOP (COT)

    #COT = find(allBackOffs > 25).cT#  4.2.7.3.2.4 Priority Classes, EN 301 893
    #list index is the matlab index -1
    #dont know if it needs to be transposed
    COT = [i for i,x in enumerate(allBackOffs) if x > 25]

    #TxopDurations = zeros(length(COT), 1)
    #dont know if it needs to be transposed
    TxopDurations = np.zeros(length(COT))
    for ii in range[1:length(COT)]:
#trace locs ----> detectPacketLocations
#detectPacketLocations line 22 cData = iData + 1j * qData; typo???
#dont understand how does locs work
        TxopDurations[ii - 1] = (locs(COT(ii), 2) - locs(COT(ii - 1) + 1, 1))
#dont understand this line below as well
    #TxopDurations(TxopDurations == 0) = [];
    [x for x in TxopDurations if x == 0]= [];

    TxopDurations = [ x / 1e3 for x in TxopDurations)   #mSec;

    # plot TXOP hist
    figName ='xx'
    __switch_0__ = priorityClass
    if 0:
        pass
    elif __switch_0__ == 0:
        figName = 'vo'
    elif __switch_0__ == 1:
        figName = 'vi'
    elif __switch_0__ == 2:
        figName = 'be'
    elif __switch_0__ == 3:
        figName = 'bg'

#######not finished#######
#assume Shady has converted the plot function:)
    textf = [num2str(length(TxopDurations)) ' Samples'];
    gtitle = ['TXOP duration Histogram, ' textf];
    xlab = 'time (mSec)';
    #is bar chark the same as Histogram? didnt convert next two lines
    histScales(4, TxopDurations, 50, gtitle, xlab, 0.05, mcat([0, ceil(max(TxopDurations))]))
    saveas(gcf,['tx_' figName '.jpg'])

    #plt.xlabel('time (mSec)')

#######################
    slotTime = 9
    __switch_1__ = priorityClass
    if 0:
        pass
    elif __switch_1__ == 0:            # voice
        kp1 = 5
        mind = 32
        maxd = 59
    elif __switch_1__ == 1:            # video
        kp1 = 9
        mind = 32
        maxd = 95
    elif __switch_1__ == 2:            # Best Effort
        kp1 = 17
        mind = 41
        maxd = 176
    elif __switch_1__ == 3:            # Background
        kp1 = 17
        mind = 77
        maxd = 212



    # Classification of Idle Periods (B)
    blen = len(BackOffs)
    #B = zeros(kp1, 1)
    #dont know if this implementation fits the other functions B =zeros(1,kp1)
    #dont know if it needs to be transposed
    B = np.zeros(kp1)
    for i in range(0:blen):
        x = BackOffs[i]
        if x < mind:
            B[0] = B[0] + 1
        elif x >= maxd:
            B[kp1-1] = B[kp1-1] + 1
        else:
            index = ceil((x - mind) / slotTime) + 1
            #not sure if this needs to -1
            B[index-1] = B[index-1] + 1


    # Calculate the observed cumulative probabilities (p)
    E = blen                    # total observed periods
    #dont know if this implementation fits the other functions p =zeros(1,kp1)
    #dont know if it needs to be transposed
    p = np.zeros(kp1)
    pMax = p

    for ii in range(0:kp1):
        p[ii] = sum(B[0:ii]) / E


    pMax[0] = 0.05
    pMax[kp1-1] = 1
    __switch_2__ = priorityClass
    if 0:
        pass
    elif __switch_2__ == 0:                            # voice
        #n = 1:3; in matlab
        #pMax(n + 1).lvalue = pMax(1) + n * 0.25
        for i in range(0,kp1-2):
            pMax[i+1]= pMax[1] + ( i + 1 ) * 0.25
    elif __switch_2__ == 1:                            # video
        pMax[1] = 0.18
        # n = 2:6;  % the document says 2:6, could be a typo, I think it is 2:7
        # pMax(n+1) = pMax(2) + (n-1) * 0.125;
        for i in range(1,kp1-3):
            pMax[i+1]= pMax[1] + i * 0.125
        pMax[kp1 - 2] = 1
    elif __switch_2__ == 2 or 3:
        pMax[1] = 0.12
        # n = 2:15;
        # pMax(n+1) = pMax(2) + (n-1) * 0.0625;
        for i in range(1,kp1-1):
            pMax[i+1]= pMax[1] + i * 0.0625


    #% Decision
    if (sum(p > pMax)):
        print('(Unit does not Comply with the Standard)')
    else:
        print('(Unit Complies with the Standard)')

#could be wrong...
    #% Plot comparison with threshold
    plt.figure(3)
    plt.bar([0:kp1 - 1],[p, pMax])
    # legend('Bin Probability','Compliance Upper threshold','Location','northwest')
    # title('Bin Probability and Threshold');
    # xlabel('Bin');
    plt.legend('Bin Probability','Compliance Upper threshold','Location','northwest')
    plt.title('Bin Probability and Threshold')
    plt.xlabel('Bin')
    #plt.savefig('prob_' figName '.jpg')
    plt.show()
    return (B, p, pMax, TxopDurations)
