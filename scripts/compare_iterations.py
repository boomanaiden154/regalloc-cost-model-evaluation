# This script is designed to compare between two iterations that are composed
# of the same binaries (i.e., created by test_file_existing_compiles.sh).
# Usage is python3 compare_iterations.py <results.txt> <results.txt>

import sys
import statistics

def getTimesFromResultsFile(fileName):
  times = []
  with open(fileName) as resultsFile:
    for resultPair in resultsFile:
      resultPairParts = resultPair.split(',')
      # Append the second part (the time rather than the cost model prediction)
      times.append(float(resultPairParts[1]))
  return times

if __name__ == '__main__':
  if(len(sys.argv) != 3):
    print("Usage is python3 compare_iterations.py <results.txt> <results.txt")
  timesFile1 = getTimesFromResultsFile(sys.argv[1])
  timesFile2 = getTimesFromResultsFile(sys.argv[2])
  differences = []
  for timePair in zip(timesFile1, timesFile2):
    differences.append(abs(timePair[1] - timePair[0]))
  print(statistics.mean(differences))