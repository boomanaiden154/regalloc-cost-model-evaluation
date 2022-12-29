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
    -DLLVM_ENABLE_RTTI=ON \
    -DCMAKE_INSTALL_PREFIX=/llvm-install \
    -C /tflite/tflite.cmake \
    ../llvm
RUN cmake --build .
RUN cmake --build . --target install
RUN mkdir /llvm-corpus
WORKDIR /llvm-corpus
RUN cmake -G Ninja \
    -DCMAKE_BUILD_TYPE=Release \
    -DLLVM_ENABLE_PROJECTS="clang" \
    -DCMAKE_C_FLAGS="-Xclang -fembed-bitcode=all" \
    -DCMAKE_CXX_FLAGS="-Xclang -fembed-bitcode=all" \
    -DCMAKE_EXPORT_COMPILE_COMMANDS=ON \
    -DCMAKE_C_COMPILER=/llvm-project/build/bin/clang \
    -DCMAKE_CXX_COMPILER=/llvm-project/build/bin/clang++ \
    -C /tflite/tflite.cmake \
    /llvm-project/llvm
RUN cmake --build .
RUN mkdir /corpus
WORKDIR /ml-compiler-opt
ENV PYTHONPATH=/ml-compiler-opt
RUN python3 compiler_opt/tools/extract_ir.py \
    --cmd_filter="^-O2|-O3$" \
    --input=/llvm-corpus/compile_commands.json \
    --input_type=json \
    --llvm_objcopy_path=/llvm-project/build/bin/llvm-objcopy \
    --output_dir=/corpus
RUN python3 compiler_opt/tools/generate_default_trace.py \
    --data_path=/corpus \
    --output_path=/default_trace \
    --gin_files=compiler_opt/rl/regalloc/gin_configs/common.gin \
    --gin_bindings=config_registry.get_configuration.implementation=@configs.RegallocEvictionConfig \
    --gin_bindings=clang_path="'/llvm-project/build/bin/clang'" \
    --sampling_rate=0.01
RUN sed -i 's/10000/20/g' compiler_opt/rl/regalloc/gin_configs/behavioral_cloning_nn_agent.gin
RUN PYTHONPATH=$PYTHONPATH:. python3 compiler_opt/rl/train_bc.py \
    --root_dir=/warmstart \
    --data_path=/default_trace \
    --gin_files=compiler_opt/rl/regalloc/gin_configs/behavioral_cloning_nn_agent.gin
WORKDIR /
RUN apt-get update && apt-get install -y libunwind-dev libgflags-dev libssl-dev libelf-dev protobuf-compiler
RUN git clone --recursive https://github.com/google/autofdo
WORKDIR /autofdo
RUN git checkout 2c1e143d2a7c8545d5f1b7c625d9cde7fcb0db65
COPY ./patches/autofdo-* ./
RUN git apply autofdo-*.patch
RUN mkdir -p /autofdo/build
WORKDIR /autofdo/build
RUN cmake -G Ninja \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_INSTALL_PREFIX=. \
    -DLLVM_PATH=/llvm-install \
    ../
RUN cmake --build .
WORKDIR /
RUN apt-get update && apt-get install -y flex bison
RUN git clone --depth 1 https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git
WORKDIR /linux/tools/perf
RUN make
RUN cp perf /usr/bin
COPY . /regalloc-testing
WORKDIR /
RUN apt-get update && apt-get install -y time
RUN git clone https://github.com/andikleen/pmu-tools
