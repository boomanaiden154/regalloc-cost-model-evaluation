import sys
import statistics

from absl import app, flags

FLAGS = flags.FLAGS

flags.DEFINE_string('input_file', None, 'The input file with times to process')
flags.DEFINE_bool('average', True, 'Whether or not to display the average value')
flags.DEFINE_bool('stdev', False, 'Whether or not to display the standard deviation')

def main(_):
    with open(FLAGS.input_file) as benchmark_file:
        raw_benchmark_results = benchmark_file.readlines()
        benchmark_results = []
        for raw_benchmark_result in raw_benchmark_results:
            benchmark_result = float(raw_benchmark_result[3:])
            benchmark_results.append(benchmark_result)
        if FLAGS.average:
            print(statistics.mean(benchmark_results))
        if FLAGS.stdev:
            print(statistics.stdev(benchmark_results))

if __name__ == '__main__':
    app.run(main)

