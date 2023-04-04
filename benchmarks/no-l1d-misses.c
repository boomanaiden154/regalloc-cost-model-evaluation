// This function should only hit L1D cache (maybe after some initial cache
// warming) as it only allocates a (couple) page(s) of memory.

#include <unistd.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
#include <stdint.h>

#ifdef CALL_COUNT_INSTRUMENTATION
static int64_t sixteenWideOperationCalls = 0;
static int64_t leftShiftCalls = 0;
static int64_t mainCalls = 1;
#endif

// Ths function assumes that arraySize is a multiple of 8
#ifdef ALWAYS_INLINE
__attribute__((always_inline))
#else
__attribute__((noinline))
#endif
static void sixteenWideOperation(long* inputArray, size_t arraySize) {
#ifdef CALL_COUNT_INSTRUMENTATION
  ++sixteenWideOperationCalls;
#endif
  long a = 0;
  long b = 0;
  long c = 0;
  long d = 0;
  long e = 0;
  long f = 0;
  long g = 0;
  long h = 0;
  long a1 = 0;
  long b1 = 0;
  long c1 = 0;
  long d1 = 0;
  long e1 = 0;
  long f1 = 0;
  long g1 = 0;
  long h1 = 0;
  for(int i = 0; i < arraySize; i += 16) {
    a += inputArray[i + 0];
    b += inputArray[i + 1];
    c += inputArray[i + 2];
    d += inputArray[i + 3];
    e += inputArray[i + 4];
    f += inputArray[i + 5];
    g += inputArray[i + 6];
    h += inputArray[i + 7];
    a1 += inputArray[i + 8];
    b1 += inputArray[i + 9];
    c1 += inputArray[i + 10];
    d1 += inputArray[i + 11];
    e1 += inputArray[i + 12];
    f1 += inputArray[i + 13];
    g1 += inputArray[i + 14];
    h1 += inputArray[i + 15];
    long result = (a + b) + (c - d) + (e * f) + (g * h);
    long result2 = (a1 + b1) + (c1 - d1) + (e1 * f1) + (g1 * h1);
    // cap values to try and prevent overflows
    if (result > 100000) {
      result = 500;
    } else if (result < -100000) {
      result = -500;
    }

    if (result2 > 100000) {
      result2 = 500;
    } else if (result < -100000) {
      result2 = -500;
    }
    inputArray[i + 0] = result + result2;
  }
}

#ifdef ALWAYS_INLINE
__attribute__((always_inline))
#else
__attribute__((noinline))
#endif
static void leftShift(long* inputArray, size_t arraySize) {
#ifdef CALL_COUNT_INSTRUMENTATION
  ++leftShiftCalls;
#endif
  long tempValue = inputArray[0];
  for(int i = 1; i < arraySize; ++i) {
    long tempValue2 = inputArray[i];
    inputArray[i] = tempValue;
    tempValue = tempValue2;
  }
  inputArray[0] = tempValue;
}

int main() {
  int pageSize = getpagesize();
  size_t arraySize = (1 * pageSize) / sizeof(long);
  long* longArray = (long*)mmap(NULL, arraySize * sizeof(long), PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
  memset(longArray, 5, arraySize);
  for(int i = 0; i < 2500000; ++i) {
      sixteenWideOperation(longArray, arraySize);
      leftShift(longArray, arraySize);
  }
  munmap(longArray, arraySize * sizeof(long));
#ifdef CALL_COUNT_INSTRUMENTATION
  printf("sixteenWideOperation,%ld\n", sixteenWideOperationCalls);
  printf("leftShift,%ld\n", leftShiftCalls);
  printf("main,%ld\n", mainCalls);
#else
  printf("current page size:%d\n", pageSize);
  printf("allocated memory is at:%ld\n", (long)longArray);
  printf("array size:%ld\n", arraySize);
#endif
  return 0;
}
