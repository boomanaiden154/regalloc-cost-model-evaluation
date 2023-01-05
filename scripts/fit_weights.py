# This script takes in raw regalloc scoring data (ie not concatenated with
# weights) and timing data and then fits new weights to try and best predict
# the timing data.
# Generate the raw data from a set of results from test_file.sh with
# combined_regalloc_raw.sh
# Usage: python3 fit_weights.py <combined_regalloc_raw.sh output>

import sys
import pandas

from sklearn import linear_model

from evaluate_no_weights import evaluateModel

if __name__ == '__main__':
    if(len(sys.argv) != 2):
        print("Usage is python3 fit_weights.py <combined_regalloc_raw.sh>")
    df = pandas.read_csv(sys.argv[1], names=["copies","loads","stores","loadstores","expensiveremats","cheapremats","time"])
    X = df[["copies","loads","stores","expensiveremats","cheapremats"]]
    # add loads and stores from loadStores
    X = X.assign(loads=(X["loads"] + df["loadstores"]))
    X = X.assign(stores=(X["stores"] + df["loadstores"]))
    # Scale the time so we don't get extremely small coefficients
    y = df["time"] * 10 ** 9
    regression = linear_model.LinearRegression()
    regression.fit(X, y)
    coefficients = regression.coef_
    print(f"Multivariable regression coefficients:{coefficients}")
    print(f"Multivariable regression intercept:{regression.intercept_}")
    # normalize coefficients
    normalizationFactor = 1 / coefficients[0]
    normalizedCoefficients = []
    for coefficient in coefficients:
        normalizedCoefficients.append(coefficient * normalizationFactor)
    print(f"Normalized coefficients:{normalizedCoefficients}")
    print(f"Unadjusted R^2 value:{regression.score(X,y)}")
    predictedValues = regression.predict(X)
    scoreTimePairs = []
    for i in range(0,len(predictedValues)):
        score = predictedValues[i]
        time = df["time"][i]
        scoreTimePairs.append((score,time))
    newModelEvaluated = evaluateModel(scoreTimePairs)
    print(f"Post regression polarity correct:{newModelEvaluated[0]}")
    print(f"Post regression average difference:{newModelEvaluated[1]}")
