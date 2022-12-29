#include <stdio.h>
#include <stdint.h>

#define N 11

static int64_t fact[32];

#ifdef CALL_COUNT_INSTRUMENTATION
static int64_t initializeFactCalls = 0;
static int64_t rotateCalls = 0;
static int64_t createPermutationCalls = 0;
static int64_t permutationAdvanceCalls = 0;
static int64_t swapCalls = 0;
static int64_t permutationCountFlipsCalls = 0;
static int64_t mainCalls = 1;
#endif

__attribute__((noinline))
void initializeFact(int n) {
#ifdef CALL_COUNT_INSTRUMENTATION
    ++initializeFactCalls;
#endif
    fact[0] = 1;
    for (int i = 1; i <= n; ++i) {
        fact[i] = i * fact[i - 1];
    }
}

typedef struct {
    int count[N];
    int8_t current[N];
} Permutation;

__attribute__((noinline))
void rotate(int8_t* start, int8_t* middle, int8_t* end) {
#ifdef CALL_COUNT_INSTRUMENTATION
    ++rotateCalls;
#endif
    int finalData[end - start];
    // process the first part
    for(int i = 0; i < end - middle; ++i) {
        finalData[i] = middle[i];
    }
    // process the second part
    for(int i = 0; i < middle - start; ++i) {
        finalData[end - middle + i] = start[i];
    }
    // copy over values
    for(int i = 0; i < end - start; ++i) {
        start[i] = finalData[i];
    }
}

__attribute__((noinline))
Permutation createPermutation(int n, int64_t start) {
#ifdef CALL_COUNT_INSTRUMENTATION
    ++createPermutationCalls;
#endif
    Permutation toReturn;

    for(int i = n - 1; i >= 0; --i) {
        int64_t d = start / fact[i];
        start = start % fact[i];
        toReturn.count[i] = d;
    }

    for(int i = 0; i < n; ++i) {
        toReturn.current[i] = i;
    }

    for(int i = n - 1; i >= 0; --i) {
        int d = toReturn.count[i];
        int8_t* b = toReturn.current;
        rotate(b, b + d, b + i + 1);
    }

    return toReturn;
}

__attribute__((noinline))
void permutationAdvance(Permutation* input) {
#ifdef CALL_COUNT_INSTRUMENTATION
    ++permutationAdvanceCalls;
#endif
    for(int i = 1; ; ++i) {
        int8_t first = input->current[0];
        for(int j = 0; j < i; ++j) {
            input->current[j] = input->current[j + 1];
        }
        input->current[i] = first;

        ++(input->count[i]);
        if (input->count[i] <= i) {
            break;
        }
        input->count[i] = 0;
    }
}

__attribute__((noinline))
void swap(int8_t* a, int8_t* b) {
#ifdef CALL_COUNT_INSTRUMENTATION
    ++swapCalls;
#endif
    int8_t temp = *a;
    *a = *b;
    *b = temp;
}

__attribute__((noinline))
int64_t permutationCountFlips(Permutation* input) {
#ifdef CALL_COUNT_INSTRUMENTATION
    ++permutationCountFlipsCalls;
#endif
    int flips = 0;
    int8_t first = input->current[0];

    if (first > 0) {
        flips = 1;

        int8_t temp[N];

        for(int i = 0; i < N; ++i) {
            temp[i] = input->current[i];
        }

        for(; temp[first] > 0; ++flips) {
            int8_t newFirst = temp[first];
            temp[first] = first;

            if(first > 2) {
                int64_t low = 1, high = first - 1;
                do {
                    swap(temp + low, temp + high);
                    if(!(low + 3 <= high && low < 16)) {
                        break;
                    }
                    ++low;
                    --high;
                } while (1);
            }
            first = newFirst;
        }
    }
    return flips;
}

int main() {
    initializeFact(N);

    int blockCount = 24;
    if(blockCount > fact[N]) {
        blockCount = 1;
    }
    int64_t blockLength = fact[N] / blockCount;

    int64_t maxFlips = 0, checksum = 0;

    for(int64_t blockStart = 0; blockStart < fact[N]; blockStart += blockLength) {
        Permutation permutation = createPermutation(N, blockStart);

        int64_t index = blockStart;

        while(1) {
            const int64_t flips = permutationCountFlips(&permutation);

            if(flips) {
                if(index % 2 == 0) {
                    checksum += flips;
                } else {
                    checksum -= flips;
                }

                if(flips > maxFlips) {
                    maxFlips = flips;
                }
            }

            if(++index == blockStart + blockLength) {
                break;
            }

            permutationAdvance(&permutation);
        }
    }

#ifdef CALL_COUNT_INSTRUMENTATION
    printf("initializeFact,%ld\n", initializeFactCalls);
    printf("rotate,%ld\n", rotateCalls);
    printf("createPermutation,%ld\n", createPermutationCalls);
    printf("permutationAdvance,%ld\n", permutationAdvanceCalls);
    printf("swap,%ld\n", swapCalls);
    printf("permutationCountFlips,%ld\n", permutationCountFlipsCalls);
    printf("main,%ld\n", mainCalls);
#else
    printf("%ld\n", checksum);
    printf("Pfannkuchen(%d)=%ld\n", N, maxFlips);
#endif

    return 0;
}
