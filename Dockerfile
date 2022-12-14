FROM mlgo-development
RUN git clone https://github.com/llvm/llvm-project
WORKDIR /llvm-project
RUN git checkout fc21f2d7bae2e0be630470cc7ca9323ed5859892
COPY ./patches/regalloc-scoring.patch .
RUN git apply regalloc-scoring.patch
RUN mkdir build
WORKDIR /llvm-project/build
RUN cmake -G Ninja \
    -DCMAKE_BUILD_TYPE=Release \
    -DTENSORFLOW_AOT_PATH=$(python3 -c "import tensorflow; import os; print(os.path.dirname(tensorflow.__file__))") \
    -DLLVM_ENABLE_PROJECTS="clang;lld" \
    -DLLVM_ENABLE_RUNTIMES="compiler-rt" \
    -DLLVM_ENABLE_ASSERTIONS=ON \
    -C /tflite/tflite.cmake \
    ../llvm
RUN cmake --build .
COPY . /regalloc-testing
