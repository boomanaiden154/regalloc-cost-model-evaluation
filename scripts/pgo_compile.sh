set -x
set -e
if [[ ${1:(-3)} == cpp ]]
then
    compiler=/llvm-project/build/bin/clang++
else
    compiler=/llvm-project/build/bin/clang
fi
$compiler $1 -o $2-instrumented -O3 -lm \
    -fprofile-instr-generate \
    -mllvm -regalloc-enable-advisor=development \
    -mllvm -regalloc-model=$3 \
    -mllvm -regalloc-training-log=./log \
    $EXTRA_FLAGS
./$2-instrumented
/llvm-project/build/bin/llvm-profdata merge --output prof.data default.profraw
$compiler $1 -o $2 -O3 -lm \
    -fprofile-instr-use=./prof.data \
    -mllvm -regalloc-enable-advisor=development \
    -mllvm -regalloc-model=$3 \
    -mllvm -regalloc-training-log=./log \
    -mllvm -debug-only=regallocscore \
    -mllvm -regalloc-randomize-evictions \
    $EXTRA_FLAGS &> $2.regallocscoring.txt
sha1sum $2 >> checksums.txt
rm prof.data || true
rm default.profraw || true
rm $2-instrumented || true
rm log || true
