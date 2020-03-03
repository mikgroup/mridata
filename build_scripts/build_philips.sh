#! /usr/bin/env bash

# Philips to ISMRMRD
git clone https://github.com/ismrmrd/philips_to_ismrmrd.git
cd philips_to_ismrmrd
git checkout 9ef92a10454e685bab81c7fee1e18af9c15c5e3e
mkdir build
cd build
cmake ..
make
make install
