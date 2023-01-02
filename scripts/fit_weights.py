# This script takes in raw regalloc scoring data (ie not concatenated with
# weights) and timing data and then fits new weights to try and best predict
# the timing data.
# Generate the raw data from a set of results from test_file.sh with
# combined_regalloc_raw.sh
# Usage: python3 fit_weights.py <combined_regalloc_raw.sh output>

import sys
import pandas

from sklearn import linear_model

if __name__ == '__main__':
    if(len(sys.argv) != 2):
        print("Usage is python3 fit_weights.py <combined_regalloc_raw.sh>")
    df = pandas.read_csv(sys.argv[1], names=["copies","loads","stores","loadstores","expensiveremats","cheapremats","time"])
    X = df[["copies","loads","stores","loadstores","expensiveremats","cheapremats"]]
    # Scale the time so we don't get extremely small coefficients
    y = df["time"] * 10 ** 9
    regression = linear_model.LinearRegression()
    regression.fit(X, y)
    print(regression.coef_)
    print(regression.score(X,y))
    predictedValues = regression.predict(X)
    for value in predictedValues:
        print(value)
