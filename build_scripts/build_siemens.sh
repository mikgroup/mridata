#! /usr/bin/env bash

# Siemens to ISMRMRD
git clone https://github.com/ismrmrd/siemens_to_ismrmrd.git
cd siemens_to_ismrmrd
git checkout 9700a32e5a405e193426692fef6aa6110bc69b54
mkdir build
cd build
cmake ..
make
make install
