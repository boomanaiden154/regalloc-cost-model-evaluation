# This script is designed to evaluate a set of results with weights already
# applied to the individual components of the regalloc score
# Usage is python3 evaluate_no_weights.py <input file>

import sys

import scipy.stats

def evaluateModel(scoreTimePairs):
    baselineResult = scoreTimePairs[0]
    differences = []
    for scoreTimePair in scoreTimePairs[1:]:
        scoreDifference = scoreTimePair[0] / baselineResult[0]
        timeDifference = scoreTimePair[1] / baselineResult[1]
        differences.append((scoreDifference, timeDifference))
    polarityCorrect = 0
    deltaSum = 0
    for difference in differences:
        # check polarity
        if difference[0] > 1 and difference[1] > 1:
            polarityCorrect += 1
        elif difference[0] < 1 and difference[1] < 1:
            polarityCorrect += 1
        # calculate differences
        deltaSum += abs(difference[0] - difference[1])
    averageDifference = deltaSum / len(differences)
    # compute kendall's tau
    rawScores = []
    rawTimes = []
    # start at 1 so we ignore the baseline result
    for scoreTimePair in scoreTimePairs[1:]:
        rawScores.append(scoreTimePair[0])
        rawTimes.append(scoreTimePair[1])
    # TODO(boomanaiden154): following algorithm is extremely inefficient.
    # Refactor it to something better if more scalability is required.
    scoreRankings = []
    timeRankings = []
    for scoreTimePair in scoreTimePairs[1:]:
        scoreRankings.append(rawScores.index(scoreTimePair[0]))
        timeRankings.append(rawTimes.index(scoreTimePair[1]))
    tau = scipy.stats.kendalltau(scoreRankings, timeRankings)
    return (polarityCorrect, averageDifference, tau)


if __name__ == '__main__':
    if(len(sys.argv) != 2):
        print("Usage is python3 evaluate_no_weigts.py <input file>")
    with open(sys.argv[1]) as resultsFile:
        rawResults = resultsFile.readlines()
        parsedResults = []
        for rawResult in rawResults:
            components = rawResult.split(',')
            score = float(components[0])
            time = float(components[1])
            parsedResults.append((score,time))
        polarityCorrect, averageDifference, tau = evaluateModel(parsedResults)
        print(f'polarity correct:{polarityCorrect}/{len(parsedResults) - 1}')
        print(f'average difference:{averageDifference}')
        print(f'kendall\'s tau:{tau.statistic}')
