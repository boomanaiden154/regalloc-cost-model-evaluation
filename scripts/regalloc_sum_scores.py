# this script is designed to sum the individual components of the score
# across a single compilation instance and then weight all functions
# appropriately given their call counts
# python3 regalloc_sum_scores.py <regalloc scoring file> <call counts file>
# Output is on STDOUT

import sys

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage is python3 regalloc_sum_scores.py <regalloc scoring file> <call count file>")
    # load call counts
    callCounts = {}
    with open(sys.argv[2]) as callCountsFile:
        callCountsRaw = callCountsFile.readlines()
        for rawCallCount in callCountsRaw:
            components = rawCallCount.split(',')
            callCounts[components[0]] = int(components[1])

    # sum the actual scores
    # array formt is [copy, load, store, loadstore, expensiveRemat, cheapRemat]
    total = [0, 0, 0, 0, 0, 0]
    with open(sys.argv[1]) as regallocScoringFile:
        rawScores = regallocScoringFile.readlines()
        for rawScore in rawScores:
            components = rawScore.split(',')
            functionName = components[6].replace('\n','')
            callCount = callCounts[functionName]
            total[0] += float(components[0]) * callCount
            total[1] += float(components[1]) * callCount
            total[2] += float(components[2]) * callCount
            total[3] += float(components[3]) * callCount
            total[4] += float(components[4]) * callCount
            total[5] += float(components[5]) * callCount

    print(f'{total[0]},{total[1]},{total[2]},{total[3]},{total[4]},{total[5]}')
