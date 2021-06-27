#! /usr/bin/env bash

# GE to ISMRMRD
if [ -d "${SDKTOP}/lib" ]; then
    export HDF5_ROOT=$SDKTOP/3p

    mkdir ismrmrd_ge
    export ISMRMRD_HOME=/ismrmrd_ge/
    git clone https://github.com/ismrmrd/ismrmrd
    cd ismrmrd
    mkdir build
    cd build
    cmake -D build4GE=1 -D CMAKE_INSTALL_PREFIX=$ISMRMRD_HOME ..
    make
    make install
    cd ../../
    rm -rf ismrmrd

    mkdir ge-tools
    export GE_TOOLS_HOME=/ge-tools
    git clone https://github.com/ismrmrd/ge_to_ismrmrd.git
    cd ge_to_ismrmrd
    mkdir build
    cd build
    cmake -D CMAKE_INSTALL_PREFIX=$GE_TOOLS_HOME ..
    make
    make install
    cd ../../
    rm -rf ge_to_ismrmrd
fi
