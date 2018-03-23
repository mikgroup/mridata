#! /usr/bin/env bash

# Siemens to ISMRMRD
git clone https://github.com/ismrmrd/siemens_to_ismrmrd.git
cd siemens_to_ismrmrd/ && \
    mkdir build && \
    cd build && \
    cmake .. && \
    make && \
    sudo make install
