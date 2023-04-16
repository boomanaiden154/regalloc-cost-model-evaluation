# This script takes in raw regalloc scoring data (ie not concatenated with
# weights) and timing data and then fits new weights to try and best predict
# the timing data.
# Generate the raw data from a set of results from test_file.sh with
# combined_regalloc_raw.sh
# Usage: python3 fit_weights.py <combined_regalloc_raw.sh output>

import sys
import pandas

from absl import app, flags
from sklearn import linear_model

from evaluate_no_weights import evaluateModel

FLAGS = flags.FLAGS

flags.DEFINE_string("input_file", None,
                    "The path to the input file (output from combined_regalloc_raw.sh")
flags.DEFINE_enum("output", "default", ["default", "coefficients", "intercept",
                                        "cofint", "normcof", "r2", "posregpol",
                                        "posregdif", "cofintnolbr"],
                  "The output type to use")

flags.mark_flag_as_required("input_file")

def main(_):
    df = pandas.read_csv(FLAGS.input_file, names=["copies","loads","stores","loadstores","expensiveremats","cheapremats","time"])
    X = df[["copies","loads","stores","expensiveremats","cheapremats"]]
    # add loads and stores from loadStores
    X = X.assign(loads=(X["loads"] + df["loadstores"]))
    X = X.assign(stores=(X["stores"] + df["loadstores"]))
    # Scale the time so we don't get extremely small coefficients
    y = df["time"] * 10 ** 9
    regression = linear_model.LinearRegression()
    regression.fit(X, y)
    coefficients = regression.coef_
    # normalize coefficients
    normalizationFactor = 1 / coefficients[0]
    normalizedCoefficients = []
    for coefficient in coefficients:
        normalizedCoefficients.append(coefficient * normalizationFactor)
    predictedValues = regression.predict(X)
    scoreTimePairs = []
    for i in range(0,len(predictedValues)):
        score = predictedValues[i]
        time = df["time"][i]
        scoreTimePairs.append((score,time))
    newModelEvaluated = evaluateModel(scoreTimePairs)

    if FLAGS.output == "default":
        print(f"Multivariable regression coefficients:{coefficients}")
        print(f"Multivariable regression intercept:{regression.intercept_}")
        print(f"Normalized coefficients:{normalizedCoefficients}")
        print(f"Unadjusted R^2 value:{regression.score(X,y)}")
        print(f"Post regression polarity correct:{newModelEvaluated[\"polarityCorrect\"]}")
        print(f"Post regression average difference:{newModelEvaluated[\"averageDifference\"]}")
        print(f"Post regression kendall's tau:{newModelEvaluated[\"tau\"]}")
    elif FLAGS.output == "coefficients":
        print(f"{coefficients[0]} {coefficients[1]} {coefficients[2]} {coefficients[3]} {coefficients[4]}")
    elif FLAGS.output == "intercept":
        print(f"{regression.intercept_}")
    elif FLAGS.output == "cofint":
        print(f"{coefficients[0]} {coefficients[1]} {coefficients[2]} {coefficients[3]} {coefficients[4]}")
        print(f"{regression.intercept_}")
    elif FLAGS.output == "cofintnolbr":
        print(f"{coefficients[0]} {coefficients[1]} {coefficients[2]} {coefficients[3]} {coefficients[4]} {regression.intercept_}")
    elif FLAGS.output == "normcof":
        print((f"{normalizedCoefficients[0]} {normalizedCoefficients[1]}"
               f"{normalizedCoefficients[2]} {normalizedCoefficients[3]}"
               f"{normalizedCoefficients[4]}"))
    elif FLAGS.output == "r2":
        print(f"{regression.score(X,y)}")
    elif FLAGS.output == "posregpol":
        print(f"{newModelEvaluated[\"polarityCorrect\"]}")
    elif FLAGS.output == "posregdif":
        print(f"{newModelEvaluated[\"averageDifference\"]}")

if __name__ == "__main__":
    app.run(main)
