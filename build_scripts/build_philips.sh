#! /usr/bin/env bash

# Philips to ISMRMRD
git clone https://github.com/ismrmrd/philips_to_ismrmrd.git
cd philips_to_ismrmrd
mkdir build
cd build
cmake ..
make
make install
