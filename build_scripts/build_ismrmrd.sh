#! /usr/bin/env bash

apt-get update
apt-get -y install cmake g++ git-core libboost-all-dev libfftw3-dev libhdf5-serial-dev
git clone https://github.com/ismrmrd/ismrmrd
cd ismrmrd
mkdir build
cd build
cmake ../
make
make install
cd ../../
rm -rf ismrmrd
