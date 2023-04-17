# This script is designed to evaluate a set of results with weights already
# applied to the individual components of the regalloc score
# Usage is python3 evaluate_no_weights.py <input file>

import sys
import operator

import scipy.stats

from absl import app, flags

FLAGS = flags.FLAGS

flags.DEFINE_string("input_file", None, "The path to the input file")
flags.DEFINE_enum("output", "default", ["default", "polarityvector"], "The output type")

flags.mark_flag_as_required("input_file")

def getDifferences(scoreTimePairs):
    baselineResult = scoreTimePairs[0]
    differences = []
    for scoreTimePair in scoreTimePairs[1:]:
        scoreDifference = scoreTimePair[0] / baselineResult[0]
        timeDifference = scoreTimePair[1] / baselineResult[1]
        differences.append((scoreDifference, timeDifference))
    return differences

def getPolarityCorrect(differences):
    polarityCorrect = []
    for index, difference in enumerate(differences):
        # check polarity
        if difference[0] > 1 and difference[1] > 1:
            polarityCorrect.append(1)
        elif difference[0] < 1 and difference[1] < 1:
            polarityCorrect.append(1)
        else:
            polarityCorrect.append(0)
    return polarityCorrect

def getPolarityCorrectSortedArray(polarityCorrectVector, rawTimes):
    polarityTimeArray = []
    for polarityTimeTuple in zip(polarityCorrectVector, rawTimes):
        polarityTimeArray.append(polarityTimeTuple)
    polarityTimeArray.sort(key=operator.itemgetter(1))
    return polarityTimeArray

def evaluateModel(scoreTimePairs):
    # sort score time pairs by the time to make downstream
    # analysis easier
    differences = getDifferences(scoreTimePairs)
    polarityCorrectVector = getPolarityCorrect(differences)
    polarityCorrect = sum(polarityCorrectVector)
    deltaSum = 0
    for difference in differences:
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
    tau = scipy.stats.kendalltau(rawScores, rawTimes, variant='c')
    polarityCorrectSortedArray = getPolarityCorrectSortedArray(polarityCorrectVector, rawTimes)
    outputMap = {
        "polarityCorrect": polarityCorrect,
        "averageDifference": averageDifference,
        "tau": tau,
        "polarityCorrectSortedArray": polarityCorrectSortedArray
    }
    return outputMap

def main(_):
    with open(FLAGS.input_file) as resultsFile:
        rawResults = resultsFile.readlines()
        parsedResults = []
        for rawResult in rawResults:
            components = rawResult.split(',')
            score = float(components[0])
            time = float(components[1])
            parsedResults.append((score,time))
        output = evaluateModel(parsedResults)
        if FLAGS.output == "default":
            print(f'polarity correct:{output["polarityCorrect"]}/{len(parsedResults) - 1}')
            print(f'average difference:{output["averageDifference"]}')
            print(f'kendall\'s tau:{output["tau"]}')
        elif FLAGS.output == "polarityvector":
            for polarityTuple in output["polarityCorrectSortedArray"]:
                print(f"{polarityTuple[0]},{polarityTuple[1]}")

if __name__ == "__main__":
    app.run(main)
