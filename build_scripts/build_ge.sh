#! /usr/bin/env bash

# GE to ISMRMRD
if [ -d "${SDKTOP}/lib" ]; then
    git clone https://github.com/frankong/ge_to_ismrmrd.git
    cd ge_to_ismrmrd
    git checkout 338010184480d033346b4361fedb661afd7a3537
    mkdir build
    cd build
    cmake -D OX_INSTALL_DIRECTORY=$SDKTOP ..
    make
    make install
fi
