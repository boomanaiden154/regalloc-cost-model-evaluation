# This script is designed to evaluate a set of results from raw regalloc
# scores with a predetermined set of weights
# Usage is python3 evaluate_weights.py <weights separated by spaces> \
#                                      <bias> \
#                                      <raw regalloc file>

import sys

from evaluate_no_weights import evaluateModel

def evaluateWithWeights(copyWeight,
                        loadWeight,
                        storeWeight,
                        expensiveRematWeight,
                        cheapRematWeight,
                        intercept,
                        rawRegallocFileName): 
    scores = []
    times = []
    with open(rawRegallocFileName) as rawRegallocFile:
        rawRegallocScores = rawRegallocFile.readlines()
        for rawRegallocScore in rawRegallocScores:
            components = rawRegallocScore.split(",")
            copyCount = float(components[0])
            loadCount = float(components[1])
            storeCount = float(components[2])
            loadStoreCount = float(components[3])
            expensiveRematCount = float(components[4])
            cheapRematCount = float(components[5])
            score = copyWeight * copyCount
            score += loadWeight * loadCount
            score += storeWeight * storeCount
            score += (loadWeight + storeWeight) * loadStoreCount
            score += expensiveRematWeight * expensiveRematCount
            score += cheapRematWeight * cheapRematCount
            score += intercept
            time = float(components[6])
            scores.append(score)
            times.append(time)
    scoreTimePairs = []
    for score, time in zip(scores, times):
        scoreTimePairs.append((score,time))
    return evaluateModel(scoreTimePairs) + (len(scoreTimePairs),)

if __name__ == '__main__':
    if len(sys.argv) != 8:
        print("usage: python3 evaluate_weights.py <weights separated by spaces> \\")
        print("                                   <bias> \\")
        print("                                   <raw regalloc file> \\")
    copyWeight = float(sys.argv[1])
    loadWeight = float(sys.argv[2])
    storeWeight = float(sys.argv[3])
    expensiveRematWeight = float(sys.argv[4])
    cheapRematWeight = float(sys.argv[5])
    bias = float(sys.argv[6])
    rawRegallocFileName = sys.argv[7]

    outputTuple = evaluateWithWeights(copyWeight,
                                      loadWeight,
                                      storeWeight,
                                      expensiveRematWeight,
                                      cheapRematWeight,
                                      bias,
                                      rawRegallocFileName)

    polarityCorrect, averageDifference, tau, sampleSize = outputTuple

    print(f"polarity correct:{polarityCorrect}/{sampleSize - 1}")
    print(f"average difference:{averageDifference}")
