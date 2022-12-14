set -x
/llvm-project/build/bin/clang++ $1 -o $2-instrumented -O3 \
    -fprofile-instr-generate \
    -mllvm -regalloc-enable-advisor=development \
    -mllvm -regalloc-model=$3 \
    -mllvm -regalloc-training-log=./log
./$2-instrumented
/llvm-project/build/bin/llvm-profdata merge --output prof.data default.profraw
/llvm-project/build/bin/clang++ $1 -o $2 -O3 \
    -fprofile-instr-use=./prof.data \
    -mllvm -regalloc-enable-advisor=development \
    -mllvm -regalloc-model=$3 \
    -mllvm -regalloc-training-log=./log \
    -mllvm -debug-only=regallocscore \
    -mllvm -regalloc-randomize-evictions &> $2.regallocscoring.txt
sha1sum $2 >> checksums.txt
rm prof.data
rm default.profraw
rm $2-instrumented
rm log
