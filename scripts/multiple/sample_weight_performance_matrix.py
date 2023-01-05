# This script is designed to evaluate the performance of each sample's weights
# against all of the other samples.
# Each row corresponds to the optimal regression parameters from one sample

from absl import app, flags

from evaluate_weights import evaluateWithWeights

FLAGS = flags.FLAGS

flags.DEFINE_string("params_file", None,
                    "The file containing the model parameters for each sample")
flags.DEFINE_string("output_file", "outpt.txt", "The output file")
flags.DEFINE_bool("is_csv", False, "Whether or not to outpt in CSV format")

flags.mark_flag_as_required("params_file")

def main(_):
    # load params file
    perSampleParams = []
    with open(FLAGS.params_file) as paramsFile:
        params = paramsFile.readlines()
        for paramSet in params:
            components = paramSet.split(" ")
            sampleParams = {
                "copyWeight": float(components[0]),
                "loadWeight": float(components[1]),
                "storeWeight": float(components[2]),
                "expensiveRematWeight": float(components[3]),
                "cheapRematWeight": float(components[4]),
                "intercept": float(components[5]),
            }
            perSampleParams.append(sampleParams)
    # ends up being a two dimensional array
    results = []
    for sampleParams in perSampleParams:
        currentSampleResults = []
        for i in range(1,31):
            sampleParams["rawRegallocFileName"] = f"iteration-{i}/test-combined.txt"
            currentTestOutput = evaluateWithWeights(**sampleParams)
            currentSampleResults.append(currentTestOutput[0] / (currentTestOutput[2] - 1))
        results.append(currentSampleResults)
    for row in results:
        for index, column in enumerate(row):
            if index == len(row) - 1:
                separator = "\n"
            else:
                separator = "," if FLAGS.is_csv else " "
            print("{:.2f}".format(column), end=separator)

if __name__ == '__main__':
    app.run(main)
