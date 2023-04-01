FROM mlgo-development
# install dependencies
RUN apt-get update && apt-get install -y libunwind-dev \
  libgflags-dev \
  libssl-dev \
  libelf-dev \
  protobuf-compiler \
  flex \
  bison \
  time
# clone and build LLVM at specified checkout with patches
RUN git clone https://github.com/llvm/llvm-project
WORKDIR /llvm-project
RUN git checkout 6cef325481a8efc039ae9df5630609fd3a84560c
COPY ./patches/llvm-*.patch ./
RUN git apply llvm-*.patch
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
# build and install userspace perf tools
WORKDIR /
RUN git clone --depth 1 https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git
WORKDIR /linux/tools/perf
RUN make
RUN cp perf /usr/bin
WORKDIR /
# download pmu-tools
RUN git clone https://github.com/andikleen/pmu-tools
# Install/setup uiCA
RUN apt-get update && apt-get install -y gcc python3 python3-pip graphviz && pip3 install plotly
RUN git clone https://github.com/andreas-abel/uiCA.git
WORKDIR /uiCA
COPY ./patches/uica-*.patch ./
RUN git apply uica-*.patch
RUN ./setup.sh
WORKDIR /
COPY . /regalloc-testing
