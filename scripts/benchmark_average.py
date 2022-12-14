import sys
import statistics

if __name__ == '__main__':
    with open(sys.argv[1]) as benchmark_file:
        raw_benchmark_results = benchmark_file.readlines()
        benchmark_results = []
        for raw_benchmark_result in raw_benchmark_results:
            benchmark_result = float(raw_benchmark_result[3:])
            benchmark_results.append(benchmark_result)
        print(statistics.mean(benchmark_results))