// This function should only hit L1D cache (maybe after some initial cache
// warming) as it only allocates a (couple) pages of memory.

#include <unistd.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>

// Ths function assumes that arraySize is a multiple of 8
#ifdef ALWAYS_INLINE
__attribute__((always_inline))
#else
__attribute__((noinline))
#endif
void eightWideOperation(int* inputArray, size_t arraySize) {
  for(int i = 0; i < arraySize; i += 8) {
    int a = inputArray[i + 0];
    int b = inputArray[i + 1];
    int c = inputArray[i + 2];
    int d = inputArray[i + 3];
    int e = inputArray[i + 4];
    int f = inputArray[i + 5];
    int g = inputArray[i + 6];
    int h = inputArray[i + 7];
    int result = (a + b) + (c - d) + (e * f) + (g * h);
    // cap values to try and prevent overflows
    if (result > 100000) {
      result = 500;
    } else if (result < -100000) {
      result = -500;
    }
    inputArray[i + 0] = result;
  }
}

#ifdef ALWAYS_INLINE
__attribute__((always_inline))
#else
__attribute__((noinline))
#endif
void leftShift(int* inputArray, size_t arraySize) {
  int tempValue = inputArray[0];
  for(int i = 1; i < arraySize; ++i) {
    int tempValue2 = inputArray[i];
    inputArray[i] = tempValue;
    tempValue = tempValue2;
  }
  inputArray[0] = tempValue;
}

int main() {
  int pageSize = getpagesize();
  printf("current page size:%d\n", pageSize);
  size_t arraySize = (1 * pageSize) / sizeof(int);
  int* intArray = (int*)mmap(NULL, arraySize * sizeof(int), PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
  printf("allocated memory is at:%ld\n", (long)intArray);
  printf("array size:%ld\n", arraySize);
  memset(intArray, 5, arraySize);
  for(int i = 0; i < 2500000; ++i) {
      eightWideOperation(intArray, arraySize);
      leftShift(intArray, arraySize);
  }
  munmap(intArray, arraySize * sizeof(int));
  return 0;
}
