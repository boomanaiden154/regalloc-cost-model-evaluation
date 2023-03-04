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
    -mllvm -regalloc-training-log=./$2.regalloclog \
    $EXTRA_FLAGS
LLVM_PROFILE_FILE=$2.profraw ./$2-instrumented
/llvm-project/build/bin/llvm-profdata merge --output $2.profdata $2.profraw
$compiler $1 -o $2 -O3 -lm \
    -fprofile-instr-use=$2.profdata \
    -mllvm -regalloc-enable-advisor=development \
    -mllvm -regalloc-model=$3 \
    -mllvm -regalloc-training-log=./$2.regalloclog \
    -mllvm -debug-only=regallocscore \
    -mllvm -regalloc-randomize-evictions \
    -fbasic-block-sections=labels \
    $EXTRA_FLAGS &> $2.regallocscoring.txt
sha1sum $2 >> checksums.txt
rm $2.profdata
rm $2.profraw
rm $2-instrumented
rm $2.regalloclog
